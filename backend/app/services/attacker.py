import os
import asyncio
import json
from urllib.parse import urlparse
from browser_use import Agent, Browser
from browser_use.llm.google.chat import ChatGoogle
from app.services.logger import log_to_db

async def run_attack(url: str, run_id: str):
    parsed_url = urlparse(url)
    target_domain = parsed_url.netloc
    
    log_to_db(run_id, f"Target acquired: {url}", "info")
    log_to_db(run_id, f"Scope restricted to: {target_domain}", "info")
    log_to_db(run_id, "Initializing agent...", "info")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        log_to_db(run_id, "CRITICAL: GOOGLE_API_KEY not found.", "error")
        return

    findings = {
        "target": url,
        "pages_visited": [],
        "inputs_found": [],
        "inputs_tested": [],
        "vulnerabilities": [],
        "recommendations": [],
        "summary": "",
        "risk_level": "LOW",
        "steps_completed": 0
    }

    def on_step_complete(browser_state, agent_output, step_number):
        findings["steps_completed"] = step_number
        current_url = browser_state.url if hasattr(browser_state, 'url') else "Unknown"
        if current_url and current_url not in findings["pages_visited"]:
            findings["pages_visited"].append(current_url)
        
        action_summary = "Processing..."
        if agent_output and hasattr(agent_output, 'action'):
            action = agent_output.action
            if action:
                action_name = type(action).__name__
                action_summary = f"{action_name}"
        
        log_to_db(run_id, f"[Step {step_number}] {action_summary} | {current_url[:50]}...", "step")

    try:
        browser = Browser(headless=False)
        
        try:
            llm = ChatGoogle(
                model="gemini-2.5-flash",
                api_key=api_key,
                max_retries=10,
                retry_base_delay=60.0,
                retry_max_delay=180.0,
            )

            agent = Agent(
                task=f"""
                Mission: Security Audit of {url}
                
                ⚠️ CRITICAL SCOPE RESTRICTION ⚠️
                - You may ONLY navigate to URLs on the domain: {target_domain}
                - Do NOT navigate to any other website
                - Do NOT use search engines
                - Do NOT click links that go to external sites
                - If you find yourself on a different domain, IMMEDIATELY navigate back to {url}
                
                STEP 1: Navigate directly to {url}
                - Type the URL directly into the address bar
                - Wait for page to load completely
                
                STEP 2: Explore the target site
                - Scroll through the main page
                - Look for navigation menus, forms, and input fields
                - Click on 2-3 internal links ONLY (stay on {target_domain})
                
                STEP 3: Test for XSS
                - Find any search box or text input
                - Enter: <script>alert('XSS')</script>
                - Check if the script is reflected in the page
                
                STEP 4: Test for SQL Injection
                - Find any login form
                - In email/username: ' OR '1'='1' --
                - In password: anything
                - Check if login is bypassed
                
                STEP 5: Look for sensitive data exposure
                - Check for visible API responses
                - Look for error messages with stack traces
                - Note any exposed credentials or tokens
                
                FINAL OUTPUT (required JSON):
                ```json
                {{
                    "summary": "Security assessment of {target_domain}",
                    "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
                    "vulnerabilities": [
                        {{"type": "XSS|SQLi|Info Disclosure", "location": "where found", "severity": "HIGH", "description": "details"}}
                    ],
                    "inputs_found": ["list of inputs discovered"],
                    "inputs_tested": [
                        {{"input": "name", "payload": "test payload", "result": "outcome"}}
                    ],
                    "pages_visited": ["only pages on {target_domain}"],
                    "recommendations": ["security fixes"]
                }}
                ```
                """,
                llm=llm,
                browser=browser,
                use_vision=False,
                register_new_step_callback=on_step_complete,
                max_failures=3,
                max_actions_per_step=2,
            )

            log_to_db(run_id, "Agent deployed. Beginning scan...", "info")
            log_to_db(run_id, "STATUS:SCANNING", "status")

            history = await agent.run(max_steps=25)
            
            final_text = history.final_result() or ""
            
            try:
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', final_text, re.DOTALL)
                if json_match:
                    report_data = json.loads(json_match.group(1))
                    findings.update(report_data)
                elif final_text.strip().startswith('{'):
                    report_data = json.loads(final_text)
                    findings.update(report_data)
                else:
                    findings["summary"] = final_text[:500] if final_text else "Scan completed."
            except (json.JSONDecodeError, Exception):
                findings["summary"] = final_text[:500] if final_text else f"Completed {findings['steps_completed']} steps."
            
            results = history.action_results()
            if not findings["summary"]:
                findings["summary"] = f"Scanned {len(findings['pages_visited'])} pages."
            
            log_to_db(run_id, "STATUS:COMPLETE", "status")
            log_to_db(run_id, f"REPORT:{json.dumps(findings)}", "report")
        
        finally:
            if hasattr(browser, 'stop'):
                await browser.stop()

    except Exception as e:
        log_to_db(run_id, f"Anomaly detected: {str(e)}", "error")
        findings["summary"] = f"Scan error: {str(e)}"
        log_to_db(run_id, "STATUS:ERROR", "status")
        log_to_db(run_id, f"REPORT:{json.dumps(findings)}", "report")
