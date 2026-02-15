# MockFactory CLI

[![PyPI version](https://badge.fury.io/py/mockfactory-cli.svg)](https://pypi.org/project/mockfactory-cli/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mockfactory-cli.svg)](https://pypi.org/project/mockfactory-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Command-line interface for [MockFactory](https://mockfactory.io) - a secure multi-language code execution sandbox.

Execute code in isolated Docker containers with comprehensive security controls, directly from your terminal.

## Features

- **Multi-Language Support**: Python, JavaScript, PHP, Perl, Go, Shell, HTML
- **Secure Execution**: All code runs in isolated containers with no network access
- **Authentication**: Login to access your account and execution history
- **Usage Tracking**: Monitor your execution limits and tier status
- **Beautiful Output**: Rich terminal formatting with syntax highlighting
- **Easy to Use**: Simple commands for quick code execution

## Installation

```bash
pip install mockfactory-cli
```

Or install from source:

```bash
git clone https://github.com/afterdarksystems/mockfactory-cli.git
cd mockfactory-cli
pip install -e .
```

## Quick Start

### Execute code inline

```bash
mockfactory run python -c "print('Hello from MockFactory!')"
```

### Execute a file

```bash
mockfactory execute script.py
```

### Auto-detect language from file extension

```bash
mockfactory execute app.js
mockfactory execute script.php
mockfactory execute program.go
```

## Commands

### Authentication

#### Sign up for a free account

```bash
mockfactory signup
```

Creates a new account with 10 free executions per day.

#### Login to your account

```bash
mockfactory login
```

#### Check authentication status

```bash
mockfactory status
```

#### Logout

```bash
mockfactory logout
```

### Code Execution

#### Run code inline

```bash
mockfactory run <language> -c "<code>"

# Examples:
mockfactory run python -c "print('Hello World')"
mockfactory run javascript -c "console.log('Hello World')"
mockfactory run php -c "echo 'Hello World';"
```

#### Run code from a file

```bash
mockfactory run <language> -f <file>

# Example:
mockfactory run python -f script.py
```

#### Execute a file (auto-detect language)

```bash
mockfactory execute <file>

# Examples:
mockfactory execute script.py      # Python
mockfactory execute app.js         # JavaScript
mockfactory execute program.go     # Go
mockfactory execute script.sh      # Shell
```

#### Set execution timeout

```bash
mockfactory run python -c "import time; time.sleep(2); print('done')" --timeout 60
```

#### Raw output mode

```bash
# Useful for piping or scripting
mockfactory run python -c "print('result')" --raw
```

### Usage & Status

#### Check your usage

```bash
mockfactory usage
```

Shows:
- Current tier (anonymous, free, pro)
- Executions used
- Remaining executions

#### View configuration

```bash
mockfactory config show
```

### Configuration

#### Set API URL

```bash
mockfactory config set api_url https://mockfactory.io
```

#### Set timeout

```bash
mockfactory config set timeout 60
```

#### Reset to defaults

```bash
mockfactory config reset
```

## Supported Languages

| Language   | Extension | Example                              |
|------------|-----------|--------------------------------------|
| Python     | `.py`     | `mockfactory execute script.py`      |
| JavaScript | `.js`     | `mockfactory execute app.js`         |
| PHP        | `.php`    | `mockfactory execute script.php`     |
| Perl       | `.pl`     | `mockfactory execute script.pl`      |
| Go         | `.go`     | `mockfactory execute program.go`     |
| Shell      | `.sh`     | `mockfactory execute script.sh`      |
| HTML       | `.html`   | `mockfactory execute page.html`      |

## Usage Tiers

| Tier           | Executions | Price     | Features                  |
|----------------|------------|-----------|---------------------------|
| Anonymous      | 5/day      | Free      | No account required       |
| Free Account   | 10/day     | Free      | Execution history         |
| Pro            | Unlimited  | $9.99/mo  | Priority support          |

Sign up for a free account:
```bash
mockfactory signup
```

Upgrade to Pro at [mockfactory.io/pricing](https://mockfactory.io/pricing)

## Examples

### Execute a Python script

```bash
mockfactory execute hello.py
```

### Run inline JavaScript

```bash
mockfactory run javascript -c "const x = [1,2,3]; console.log(x.reduce((a,b) => a+b, 0))"
```

### Execute with custom timeout

```bash
mockfactory execute long_running.py --timeout 120
```

### Check how many runs you have left

```bash
mockfactory usage
```

### Pipe output to another command

```bash
mockfactory run python -c "print('hello')" --raw | grep hello
```

### Use in shell scripts

```bash
#!/bin/bash
result=$(mockfactory run python -c "print(2+2)" --raw)
echo "The answer is: $result"
```

## Mock Resource Management (NEW in v0.2.0)

MockFactory CLI now includes powerful resource management capabilities for creating and managing mock users, groups, containers, networks, and profiles. These features enable comprehensive testing of multi-user applications, access control systems, and containerized environments.

### Hierarchical Organization Structure

MockFactory supports a complete organizational hierarchy to mirror real-world enterprise structures:

```
Organization (acme-corp)
  ├── Domains (example.com, acme.io)
  ├── Cloud Environments (dev-cloud, prod-cloud)
  │   ├── Users
  │   ├── Containers
  │   ├── Networks
  │   └── Resources
  └── Projects (UUID-based)
      └── Grouped Resources
```

Create a complete organizational structure:

```bash
# Create an organization
mockfactory organization create acme-corp --description "Acme Corporation" --plan pro

# Create domains for the organization
mockfactory domain create example.com --organization acme-corp --verified

# Create cloud environments
mockfactory cloud create dev-cloud --provider aws --organization acme-corp --region us-east-1
mockfactory cloud create prod-cloud --provider aws --organization acme-corp --region us-west-2

# Create a project to group related resources
mockfactory project create web-app --organization acme-corp --environment production

# Create users within the organizational structure
mockfactory user create john.doe \
  --email john@example.com \
  --organization acme-corp \
  --cloud dev-cloud \
  --domain example.com

# Add users to organization with roles
mockfactory organization add-user acme-corp john.doe --role admin
```

### Mock Users

Create and manage mock user accounts for testing:

```bash
# Create a mock user
mockfactory user create john.doe --email john@example.com --full-name "John Doe" --role developer

# List all mock users
mockfactory user list

# Filter by role
mockfactory user list --role admin

# Get user details
mockfactory user get john.doe

# Delete a user
mockfactory user delete john.doe --yes
```

**User Roles**: `user` (default), `admin`, `developer`

### Mock Groups

Organize mock users into groups:

```bash
# Create a group
mockfactory group create developers --description "Development team"

# List all groups
mockfactory group list

# Add user to group
mockfactory group add-user developers john.doe

# Remove user from group
mockfactory group remove-user developers john.doe
```

### Mock Containers

Create and manage mock containers with user/group bindings:

```bash
# Create a container
mockfactory container create web-app --image nginx --network frontend

# Create container bound to a user
mockfactory container create api --user john.doe --group developers

# List containers
mockfactory container list

# Filter by network or user
mockfactory container list --network frontend
mockfactory container list --user john.doe

# Bind user to existing container
mockfactory container bind-user web-app alice

# Unbind user from container
mockfactory container unbind-user web-app alice
```

### Mock Networks

Create virtual networks for containers:

```bash
# Create a network
mockfactory network create frontend --cidr 10.1.0.0/24

# Create isolated network
mockfactory network create backend --cidr 10.2.0.0/24 --isolated

# List networks
mockfactory network list
```

### Mock User Profiles

Create detailed user profiles for testing:

```bash
# Create user profile
mockfactory profile create john.doe \
  --bio "Senior Developer" \
  --avatar "https://example.com/avatar.jpg" \
  --preferences '{"theme":"dark","notifications":true}'

# Get user profile
mockfactory profile get john.doe
```

### Use Cases for Mock Resources

**Multi-Tenant Testing**
```bash
# Create tenants
mockfactory user create tenant1 --role admin
mockfactory user create tenant2 --role user

# Create tenant-specific containers
mockfactory container create app-tenant1 --user tenant1
mockfactory container create app-tenant2 --user tenant2
```

**Access Control Testing**
```bash
# Create user hierarchy
mockfactory group create admins
mockfactory group create users
mockfactory user create admin1 --role admin
mockfactory user create user1 --role user
mockfactory group add-user admins admin1
mockfactory group add-user users user1

# Test with different permission levels
mockfactory container create protected-resource --group admins
```

**Network Isolation Testing**
```bash
# Create isolated networks
mockfactory network create dmz --cidr 10.10.0.0/24 --isolated
mockfactory network create internal --cidr 10.20.0.0/24 --isolated

# Deploy containers to different networks
mockfactory container create web-server --network dmz
mockfactory container create database --network internal
```

**Integration Testing**
```bash
# Set up complete test environment
mockfactory user create testuser --email test@example.com
mockfactory group create testers
mockfactory network create testnet --cidr 172.16.0.0/24
mockfactory container create test-env --user testuser --network testnet
mockfactory profile create testuser --bio "Test Account"
```

### Resource Binding

Mock users and groups can be bound to containers and VMs, enabling:

- **User-specific environments**: Each user gets their own isolated container
- **Group-based access**: Control which users can access which resources
- **Multi-user applications**: Test applications with multiple concurrent users
- **Permission systems**: Verify access control and authorization logic
- **Realistic scenarios**: Create production-like multi-tenant environments

### Mock Mail System

Create and manage complete email testing environments:

```bash
# Create a mail server
mockfactory mail-server create smtp-server --protocol smtp --port 587 --tls

# Create mailboxes with standard folders
mockfactory mailbox create john@example.com --user john.doe --quota 1000

# Create a mail client
mockfactory mail-client create client1 --user john.doe --server smtp-server

# Send mock emails
mockfactory mailbox send john@example.com jane@example.com \
  --subject "Test Email" --body "Hello Jane!"

# List messages in inbox
mockfactory mailbox list-messages john@example.com --folder inbox
```

**Mock Mail Servers**
- Support for SMTP, IMAP, and POP3 protocols
- TLS encryption support
- Configurable host and port settings

**Mock Mailboxes**
- Standard folders: inbox, outbox, sent, bulk, drafts
- Configurable quota limits
- User binding for multi-user scenarios
- Send and receive mock emails
- Message management and listing

**Mock Mail Clients**
- Connect to mock mail servers
- Bind to mock users
- Associate with specific mailboxes

**Email Testing Use Cases**
- Test email sending and receiving workflows
- Verify email notifications in your application
- Test multi-user email scenarios
- Validate email templates and formatting
- Test attachment handling
- Integration testing for email-based features

### Mock SMS System

Test SMS-based features and notifications:

```bash
# Create an SMS provider
mockfactory sms create-provider twilio-prod --provider twilio

# Create mock phone numbers
mockfactory sms create-number +1234567890 --user john.doe --provider twilio-prod

# Send mock SMS messages
mockfactory sms send +1234567890 +0987654321 --message "Your verification code is 123456"

# List SMS messages
mockfactory sms list-messages --phone-number +1234567890
mockfactory sms list-numbers --user john.doe
```

**SMS Testing Use Cases**
- Test SMS verification workflows
- Verify two-factor authentication (2FA)
- Test SMS notifications and alerts
- Validate phone number verification
- Integration testing for SMS-based features
- Test multi-user SMS scenarios

### User Registration Workflows

Create complete user registration flows with email and SMS verification:

```bash
# Create registration workflow with email verification
mockfactory workflow create-registration signup-flow \
  --email-verification \
  --mail-server smtp-server

# Create registration workflow with SMS verification
mockfactory workflow create-registration mobile-signup \
  --sms-verification \
  --sms-provider twilio-prod

# Create workflow with both email and SMS verification
mockfactory workflow create-registration full-signup \
  --email-verification \
  --sms-verification

# Test the registration workflow
mockfactory workflow test-registration signup-flow \
  --username john.doe \
  --email john@example.com \
  --phone +1234567890
```

**Workflow Testing Use Cases**
- Test complete user onboarding flows
- Verify multi-step registration processes
- Test email and SMS verification together
- Validate user activation workflows
- Integration testing for signup features

### Mock APIs and Webhooks

Create mock REST APIs, GraphQL endpoints, and webhooks:

```bash
# Create a mock REST API
mockfactory api create user-api --type rest --base-url https://api.example.com --auth bearer

# Add endpoints to the API
mockfactory api add-endpoint user-api /users --method GET --status 200
mockfactory api add-endpoint user-api /users --method POST --response '{"id": 1, "name": "John"}'

# Create a webhook
mockfactory api create-webhook payment-hook \
  --url https://example.com/webhook \
  --events "payment.completed,payment.failed"

# Trigger a webhook event
mockfactory api trigger-webhook payment-hook \
  --event "payment.completed" \
  --payload '{"amount": 100, "currency": "USD"}'

# List API requests
mockfactory api list-requests user-api --limit 50
```

**API Testing Use Cases**
- Test API integrations without external dependencies
- Mock third-party API responses
- Test webhook event handling
- Verify API request/response flows
- Integration testing for API clients
- Test error handling and edge cases
- GraphQL query and mutation testing

### Data Generators (NEW in v0.2.0)

Generate realistic test data for users, employees, organizations, networks, and complete test scenarios:

```bash
# Generate realistic users
mockfactory generate users --count 50 --role mixed --organization acme-corp --domain acme.com

# Generate employees with departments and job titles
mockfactory generate employees --count 100 --organization acme-corp --departments "engineering,sales,hr"

# Generate organizations
mockfactory generate organizations --count 10

# Generate network configurations
mockfactory generate network-config --cloud prod-cloud --subnets 4

# Generate IAM policies
mockfactory generate iam-policies --type common --services s3,dynamodb,lambda

# Generate complete test scenarios
mockfactory generate test-scenario startup  # or enterprise, multi-cloud, dev-team

# Output formats
mockfactory generate users --count 20 --output json   # JSON output
mockfactory generate users --count 20 --output csv    # CSV output
mockfactory generate users --count 20 --output apply  # Apply directly to system
```

**Generator Output Formats**:
- `json` - JSON format (default for most commands)
- `csv` - CSV format (for users and employees)
- `apply` - Apply directly to MockFactory (creates resources)
- `files` - Write to files (for IAM policies)

**Test Scenarios**:
- `startup` - Small company (10-20 employees, simple infrastructure)
- `enterprise` - Large organization (100+ employees, multi-region)
- `multi-cloud` - Multi-cloud deployment (AWS, GCP, Azure)
- `dev-team` - Development team environment (dev, staging, prod)

**Data Generation Use Cases**:
- Populate test environments with realistic data
- Generate large datasets for performance testing
- Create consistent test data across environments
- Machine-generate users for authentication testing
- Build complex organizational structures quickly

### Utility Helpers (NEW in v0.2.0)

Perform common transformations and operations directly from the CLI:

```bash
# Binary/Hex conversion
mockfactory utilities bin2hex 11010101
mockfactory utilities hex2bin d5

# IP address operations
mockfactory utilities ip2bin 192.168.1.1
mockfactory utilities bin2ip 11000000101010000000000100000001
mockfactory utilities ip2long 192.168.1.1
mockfactory utilities long2ip 3232235777

# CIDR operations
mockfactory utilities cidr-to-range 10.0.0.0/24
mockfactory utilities ip-in-cidr 10.0.0.50 10.0.0.0/24

# Encoding/Decoding
mockfactory utilities base64-encode "Hello World"
mockfactory utilities base64-decode SGVsbG8gV29ybGQ=
mockfactory utilities url-encode "hello world & stuff"
mockfactory utilities url-decode "hello%20world%20%26%20stuff"

# Hashing
mockfactory utilities hash "Hello World" --algorithm sha256
mockfactory utilities hash "data" --algorithm md5

# UUIDs
mockfactory utilities uuid --count 5
mockfactory utilities uuid --version 4

# String operations
mockfactory utilities slugify "Hello World & Stuff!"
mockfactory utilities random-string --length 32 --charset hex
mockfactory utilities random-password --length 20

# Time operations
mockfactory utilities timestamp --format unix
mockfactory utilities timestamp --format iso8601

# JSON operations
mockfactory utilities json-minify config.json
mockfactory utilities json-pretty config.json --indent 4
mockfactory utilities json-validate config.json
```

**Available Utility Commands**:

Binary/Hex: `bin2hex`, `hex2bin`
IP Operations: `ip2bin`, `bin2ip`, `ip2long`, `long2ip`
CIDR: `cidr-to-range`, `ip-in-cidr`
Encoding: `base64-encode`, `base64-decode`, `url-encode`, `url-decode`
Hashing: `hash` (md5, sha1, sha256, sha512)
UUIDs: `uuid`
Strings: `slugify`, `random-string`, `random-password`
Time: `timestamp`
JSON: `json-minify`, `json-pretty`, `json-validate`

**Utility Use Cases**:
- Quick conversions without writing scripts
- Debugging network configurations
- Testing encoding/decoding implementations
- Generating secure passwords and tokens
- Validating data formats
- Pipeline transformations in shell scripts

## Configuration Files

Configuration is stored in `~/.mockfactory/`:

- `config.json` - CLI configuration (API URL, timeout, etc.)
- `token` - Authentication token (automatically managed)

## Security

- All code executes in isolated Docker containers
- No network access for sandbox containers
- Read-only filesystem (except `/tmp`)
- Resource limits enforced (CPU, memory, time)
- Runs as unprivileged user (`nobody`)

## Troubleshooting

### Authentication errors

If you get authentication errors, try logging out and back in:

```bash
mockfactory logout
mockfactory login
```

### Connection errors

Check your API URL configuration:

```bash
mockfactory config show
```

Reset to defaults if needed:

```bash
mockfactory config reset
```

### Rate limiting

If you've exceeded your tier's execution limit:

1. Wait for the daily reset
2. Sign up for a free account (10 runs/day)
3. Upgrade to Pro (unlimited)

## Aliases

For convenience, you can use the short alias `mf`:

```bash
mf run python -c "print('shorter!')"
mf execute script.py
mf status
```

## Development

### Setup development environment

```bash
git clone https://github.com/afterdarksystems/mockfactory-cli.git
cd mockfactory-cli
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Code formatting

```bash
black .
ruff check .
```

## Links

- Website: [mockfactory.io](https://mockfactory.io)
- Documentation: [github.com/afterdarksystems/mockfactory-cli](https://github.com/afterdarksystems/mockfactory-cli)
- Issues: [github.com/afterdarksystems/mockfactory-cli/issues](https://github.com/afterdarksystems/mockfactory-cli/issues)

## License

MIT License - see LICENSE file for details

## Support

For support, contact: support@afterdarksystems.com
