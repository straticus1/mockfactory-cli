# Changelog

All notable changes to MockFactory CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-14

### Added

#### Hierarchical Organization Structure

Complete organizational hierarchy for enterprise-level testing:

**Mock Organizations**
- `mockfactory organization create <name>` - Create organizations with plans (free, pro, enterprise)
- `mockfactory organization list` - List all organizations
- `mockfactory organization get <name>` - Get organization details
- `mockfactory organization delete <name>` - Delete organizations
- `mockfactory organization add-user <org> <user>` - Add users with roles (member, admin, owner)
- `mockfactory organization remove-user <org> <user>` - Remove users from organizations
- UUID-based organization IDs for resource grouping

**Mock Domains**
- `mockfactory domain create <domain>` - Create mock domains
- `mockfactory domain list` - List all domains
- `mockfactory domain get <domain>` - Get domain details
- `mockfactory domain verify <domain>` - Verify domain ownership
- `mockfactory domain delete <domain>` - Delete domains
- Bind domains to organizations
- DNS record configuration support

**Mock Cloud Environments**
- `mockfactory cloud create <name>` - Create cloud environments (AWS, GCP, Azure, custom)
- `mockfactory cloud list` - List all cloud environments
- `mockfactory cloud get <name>` - Get cloud details
- `mockfactory cloud delete <name>` - Delete cloud environments
- Regional support and organization binding

**Mock Projects**
- `mockfactory project create <name>` - Create projects with UUID-based project IDs
- `mockfactory project list` - List all projects
- `mockfactory project get <project-id>` - Get project and all bound resources
- `mockfactory project bind-resource <project-id> <type> <id>` - Bind resources to projects
- `mockfactory project unbind-resource <project-id> <type> <id>` - Unbind resources
- `mockfactory project delete <project-id>` - Delete projects and optionally all resources
- Environment support (development, staging, production)

#### Mock Resource Management System

Comprehensive resource management system for creating and managing mock users, groups, containers, networks, and profiles:

**Mock Users** (with hierarchical support)
- `mockfactory user create <username>` - Create mock users with email, name, and role
- Support for --organization, --cloud, --domain, and --project-id binding
- `mockfactory user list` - List all mock users with role filtering
- `mockfactory user get <username>` - Get detailed user information
- `mockfactory user delete <username>` - Delete mock users
- Users can exist within organizations, clouds, and domains

**Mock Groups**
- `mockfactory group create <name>` - Create mock groups for organizing users
- `mockfactory group list` - List all mock groups
- `mockfactory group add-user <group> <user>` - Add users to groups
- `mockfactory group remove-user <group> <user>` - Remove users from groups

**Mock Containers**
- `mockfactory container create <name>` - Create mock containers with image, network, and user bindings
- `mockfactory container list` - List containers with filtering by network or user
- `mockfactory container bind-user <container> <user>` - Bind users to containers
- `mockfactory container unbind-user <container> <user>` - Unbind users from containers

**Mock Networks**
- `mockfactory network create <name>` - Create mock networks with custom CIDR blocks
- `mockfactory network list` - List all mock networks
- Support for isolated networks

**Mock User Profiles**
- `mockfactory profile create <username>` - Create user profiles with bio, avatar, and preferences
- `mockfactory profile get <username>` - Get user profile details

**Mock Mail Servers**
- `mockfactory mail-server create <name>` - Create mock mail servers with SMTP, IMAP, or POP3 protocols
- `mockfactory mail-server list` - List all mock mail servers
- `mockfactory mail-server get <name>` - Get mail server details
- `mockfactory mail-server delete <name>` - Delete mock mail servers
- Support for TLS encryption and custom host/port configuration

**Mock Mail Clients**
- `mockfactory mail-client create <name>` - Create mock mail clients
- `mockfactory mail-client list` - List all mock mail clients with filtering
- `mockfactory mail-client delete <name>` - Delete mock mail clients
- Bind clients to users and mail servers

**Mock Mailboxes**
- `mockfactory mailbox create <email>` - Create mock mailboxes with standard folders (inbox, outbox, sent, bulk, drafts)
- `mockfactory mailbox list` - List all mock mailboxes
- `mockfactory mailbox get <email>` - Get mailbox details and folder statistics
- `mockfactory mailbox delete <email>` - Delete mock mailboxes
- `mockfactory mailbox send <from> <to>` - Send mock emails between mailboxes
- `mockfactory mailbox list-messages <email>` - List messages in mailbox folders
- Configurable quota limits and user binding

**Mock SMS System**
- `mockfactory sms create-provider <name>` - Create SMS providers (Twilio, AWS SNS, Nexmo, custom)
- `mockfactory sms list-providers` - List all SMS providers
- `mockfactory sms create-number <phone>` - Create mock phone numbers
- `mockfactory sms list-numbers` - List all phone numbers with filtering
- `mockfactory sms send <from> <to>` - Send mock SMS messages
- `mockfactory sms list-messages` - List SMS message history
- Support for multiple SMS providers and user binding

**User Registration Workflows**
- `mockfactory workflow create-registration <name>` - Create user registration workflows
- `mockfactory workflow test-registration <workflow>` - Test registration workflows
- `mockfactory workflow list` - List all workflows
- Support for email verification via mock mail servers
- Support for SMS verification via mock SMS providers
- Combined email + SMS verification workflows

**Mock APIs and Webhooks**
- `mockfactory api create <name>` - Create mock APIs (REST, GraphQL, Webhook)
- `mockfactory api add-endpoint <api> <path>` - Add endpoints to APIs
- `mockfactory api list` - List all mock APIs
- `mockfactory api list-requests <api>` - View API request history
- `mockfactory api delete <name>` - Delete mock APIs
- `mockfactory api create-webhook <name>` - Create mock webhooks
- `mockfactory api trigger-webhook <webhook>` - Trigger webhook events
- Support for multiple authentication types (none, basic, bearer, api-key)
- Configurable responses and status codes

### Features

- **Resource Binding**: Ability to bind mock users and groups to containers and VMs
- **Rich Terminal Output**: Beautiful tables and formatted output for all commands
- **Flexible Options**: Comprehensive command-line options for all resource types
- **Role-Based Users**: Support for different user roles (user, admin, developer)
- **Network Isolation**: Create isolated networks for secure testing
- **Group Management**: Hierarchical organization of users into groups

### Use Cases

The new mock resource system enables:
- **Multi-tenant testing**: Test applications with multiple user accounts
- **Access control testing**: Verify permission systems with different user roles
- **Network isolation testing**: Test network segmentation and isolation
- **Container orchestration**: Manage mock container workloads
- **User experience testing**: Create realistic user profiles for testing
- **Email workflow testing**: Test complete email sending, receiving, and notification systems
- **Multi-user email scenarios**: Verify email communication between multiple mock users
- **SMS verification testing**: Test two-factor authentication and SMS notifications
- **User registration flows**: Test complete onboarding with email/SMS verification
- **API integration testing**: Mock external APIs and test integrations
- **Webhook testing**: Test webhook event handling and processing

### Technical Details

- Commands are structured as subcommands: `mockfactory <resource> <action>`
- All commands include helpful examples in `--help` output
- Confirmation prompts for destructive operations (with `--yes` flag to skip)
- Consistent error handling and success messages
- API endpoints to be implemented in backend (currently showing informational messages)

## [0.1.0] - 2026-02-13

### Added
- Initial release of MockFactory CLI
- Code execution in secure sandboxes
- Support for 7 programming languages (Python, JavaScript, PHP, Perl, Go, Shell, HTML)
- User authentication (login, signup, logout)
- Usage tracking and status commands
- Configuration management
- Rich terminal output with syntax highlighting
- `mf` short alias for convenience

### Features
- Execute code inline with `-c` flag
- Execute files with auto-detection from extension
- Custom timeout support
- Raw output mode for scripting
- Secure token storage in `~/.mockfactory/`

[0.2.0]: https://github.com/straticus1/mockfactory-cli/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/straticus1/mockfactory-cli/releases/tag/v0.1.0
