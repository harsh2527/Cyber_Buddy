# 🕷️ WebApp CyberBuddy - Advanced Web Application Security Testing Tool

Your specialized companion for web application bug bounty hunting and penetration testing.

## Features

### 🎯 Core Capabilities
- **SQL Injection Testing** - Automated payloads with error-based and time-based detection
- **XSS Vulnerability Testing** - Reflected XSS detection with various payload types
- **Local File Inclusion (LFI)** - File path traversal and inclusion testing
- **Remote Code Execution (RCE)** - Command injection detection
- **Server Side Template Injection (SSTI)** - Template expression evaluation testing
- **XXE Vulnerabilities** - XML External Entity injection testing
- **Open Redirect Detection** - URL redirection vulnerability testing
- **IDOR Testing** - Insecure Direct Object Reference detection

### 🔍 Advanced Features
- **Multi-threaded Directory Fuzzing** - Fast directory and file discovery
- **Technology Stack Detection** - Framework and technology fingerprinting
- **Security Header Analysis** - Missing security header identification
- **Target Management** - Organized target tracking and persistence
- **Finding Management** - Vulnerability tracking with severity classification
- **Report Generation** - Professional markdown reports
- **Payload Collections** - Curated payloads for different attack types

## Quick Start

### 1. Setup
```bash
# Install dependencies
py -m pip install -r requirements.txt
```

### 2. Basic Usage
```bash
# Show help and banner
python cyber_buddy.py --banner

# Add a target
python cyber_buddy.py target add "Example Corp" "https://example.com" --type public

# List targets
python cyber_buddy.py target list

# Perform reconnaissance
python cyber_buddy.py recon "Example Corp"

# Full vulnerability scan
python cyber_buddy.py scan "Example Corp"
```

### 3. Advanced Testing
```bash
# Test specific vulnerabilities
python cyber_buddy.py web sqli "https://example.com"
python cyber_buddy.py web xss "https://example.com"
python cyber_buddy.py web lfi "https://example.com"

# Directory fuzzing with custom threads
python cyber_buddy.py fuzz "https://example.com" --threads 20

# Generate payload lists
python cyber_buddy.py payloads sqli
python cyber_buddy.py payloads xss
```

## Command Reference

### Target Management
- `target add <name> <url> [--type <type>]` - Add new target
- `target list` - List all targets

### Reconnaissance
- `recon <target>` - Full reconnaissance scan
- `fuzz <url> [--threads N]` - Directory/file fuzzing

### Vulnerability Testing
- `scan <target>` - Comprehensive vulnerability scan
- `web sqli <url>` - SQL injection testing
- `web xss <url>` - XSS vulnerability testing
- `web lfi <url>` - Local File Inclusion testing
- `web rce <url>` - Remote Code Execution testing

### Findings & Reports
- `finding add <target> <vuln_type> <severity> <description>` - Add finding
- `finding list` - List all findings
- `report <target>` - Generate report

### Utilities
- `methodology` - Show testing methodology
- `tools` - Show recommended tools
- `payloads <type>` - Generate payload files

## Security Considerations

⚠️ **Important:** This tool is for educational and authorized testing purposes only.

- Only test applications you own or have explicit permission to test
- Use responsibly and ethically
- Be mindful of rate limiting and server load
- Follow responsible disclosure practices
- Respect scope limitations in bug bounty programs

## Payload Types

The tool includes curated payloads for:
- **SQL Injection** - Error-based, union-based, time-based
- **XSS** - Script tags, event handlers, various contexts
- **LFI** - Path traversal, PHP wrappers, null byte injection
- **RCE** - Command separators, backticks, variable expansion
- **SSTI** - Template expressions for various engines
- **XXE** - External entity references for file disclosure

## Directory Structure

```
cyber_data/
├── targets.json          # Target definitions
├── findings.json         # Vulnerability findings
├── payloads/             # Generated payload files
│   ├── sqli_payloads.txt
│   ├── xss_payloads.txt
│   └── ...
└── report_*.md          # Generated reports
```

## Contributing

Feel free to contribute by:
- Adding new vulnerability testing modules
- Improving detection algorithms
- Adding new payload collections
- Enhancing reporting features
- Fixing bugs and improving performance

## Disclaimer

This tool is provided for educational and authorized security testing purposes only. Users are responsible for complying with all applicable laws and regulations. The authors are not responsible for any misuse of this tool.

## 🤖 AI Agent - Autonomous Testing

The **CyberAgent** is an intelligent AI that can autonomously perform security testing on your behalf!

### Features:
- **Autonomous Decision Making** - AI decides which tests to run based on risk assessment
- **Adaptive Strategy** - Adjusts testing approach based on server responses
- **Risk Assessment** - Automatically evaluates target risk levels
- **Smart Delays** - Adapts timing between tests to avoid overloading servers
- **Auto-Reporting** - Generates comprehensive AI-powered reports
- **Learning Mode** - Learns from test results to improve future testing

### Quick Start with AI Agent:
```bash
# Interactive mode (recommended)
py cyber_agent.py --interactive

# Or use the launcher
launch_agent.bat

# Direct testing
py cyber_agent.py --test "MyPortal,https://myportal.com" --strategy conservative
```

### AI Agent Commands:
```
CyberAgent> help                    # Show all commands
CyberAgent> test MyPortal https://example.com  # Start autonomous testing
CyberAgent> status                  # Check agent status
CyberAgent> strategy balanced       # Change testing strategy
CyberAgent> results                 # View recent test results
CyberAgent> stop                    # Stop current testing
CyberAgent> exit                    # Exit the agent
```

### Testing Strategies:
- **Conservative**: Slow, safe testing with 2-5s delays, skips dangerous tests
- **Balanced**: Moderate testing with 1-3s delays, includes most tests
- **Aggressive**: Fast testing with 0.5-2s delays, includes all tests

### AI Decision Making:
The agent makes intelligent decisions based on:
- Target risk assessment (localhost/staging/production)
- Previous test results and error rates
- Server response patterns
- Security measure detection (WAF, rate limiting)
- Risk thresholds and safety limits

### Safety Features:
- Automatic risk assessment
- Emergency stop conditions
- Rate limiting protection
- Server stress detection
- Adaptive delays

Happy hunting! 🎯
