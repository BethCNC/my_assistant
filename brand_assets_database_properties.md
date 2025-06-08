# Brand Assets Database Properties Reference

## Database Overview
- **Database Name**: Brand Assets
- **Database ID**: `18c86edc-ae2c-80d4-852c-fd7e132b780b`
- **URL**: https://www.notion.so/18c86edcae2c80d4852cfd7e132b780b
- **Type**: Inline database
- **Created**: January 31, 2025
- **Last Edited**: May 28, 2025

## Primary Properties

### Core Identification
| Property | Type | ID | Description |
|----------|------|----|-----------| 
| **Name** | `title` | `title` | Primary title/name of the brand asset |

### Asset Classification
| Property | Type | ID | Options/Details |
|----------|------|----|-----------| 
| **Type** | `select` | `x%60sp` | Categorizes the type of brand asset |
| **Asset Template** | `checkbox` | `%40n%3Ew` | Marks if this is a template asset |

#### Type Options:
- **Brand Strategy** (yellow)
- **Brand Guidelines** (yellow) 
- **Brand Asset/Template** (yellow)
- **Website Design-UI** (purple)
- **UX Research & Design** (orange)
- **UI Design System Component** (blue)
- **UI Design System Token** (blue)
- **UI Design System Other** (blue)
- **Web Development** (green)
- **Web Analytics** (green)

### Project Management
| Property | Type | ID | Options/Details |
|----------|------|----|-----------| 
| **Status** | `status` | `VAWr` | Current status with grouped workflow |
| **Stage** | `status` | `Yi%5Dc` | Project stage in development lifecycle |
| **Priority** | `select` | `eLvG` | Task priority level |
| **Client Workflow** | `multi_select` | `QCsf` | Type of client work involved |

#### Status Options (Grouped):
**To-do Group:**
- Planning (pink)
- Not started (pink)

**In Progress Group:**
- Snoozed (gray)
- In Inbox (default)
- In Progress (green)
- DO NEXT!! (blue)
- Someday Maybe (purple)
- Assigned to Client (yellow)
- Needs Client Review (yellow)
- Internal Review (orange)
- Needs Revisions (orange)
- Waiting for (brown)
- Approved (green)

**Complete Group:**
- Complete (red)
- Archive (default)

#### Stage Options (Grouped):
**In Progress Group:**
- Discovery (orange)
- Concept (yellow)
- Design (green)
- Development (blue)
- Delivery (purple)

**Complete Group:**
- Complete (red)

#### Priority Options:
- **High** (red)
- **Medium** (yellow)
- **Low** (green)

#### Client Workflow Options:
- **Brand Design** (red)
- **Web Design** (green)
- **Web Development** (orange)

### File Attachments
| Property | Type | ID | Description |
|----------|------|----|-----------| 
| **Assets** | `files` | `%7D%7DcM` | File attachments for the brand asset |
| **Cover** | `files` | `cOem` | Cover image for the asset |

### External Links
| Property | Type | ID | Description |
|----------|------|----|-----------| 
| **Figma Link** | `url` | `%7DOw~` | Link to Figma design files |

### Documentation
| Property | Type | ID | Description |
|----------|------|----|-----------| 
| **Notes** | `rich_text` | `j%3FFC` | Additional notes and documentation |

### Metadata
| Property | Type | ID | Description |
|----------|------|----|-----------| 
| **Created** | `created_time` | `Ffud` | Automatically tracks creation date |
| **Last edited** | `last_edited_time` | `%3C%7BTH` | Automatically tracks last edit time |
| **(Unnamed checkbox)** | `checkbox` | `x%7BRa` | Unnamed checkbox property |

## Related Database Relationships

### 1. Client Relationship
| Property | Type | ID | Related Database |
|----------|------|----|-----------| 
| **Client** | `relation` | `B%40m~` | Clients Database |

**Related Database**: `Clients` (`f35dd790-78dd-4a1e-99a8-ae538047976c`)
- **Synced Property**: "Brand Assets" in Clients database
- **Relationship Type**: Dual property (bidirectional)

### 2. Project Relationship  
| Property | Type | ID | Related Database |
|----------|------|----|-----------| 
| **Project** | `relation` | `ld%3DB` | Projects Database |

**Related Database**: `Projects` (`15a86edc-ae2c-81ec-b2d2-c598b0ab9f65`)
- **Synced Property**: "Brand Assets" in Projects database  
- **Relationship Type**: Dual property (bidirectional)

## Related Databases Overview

### Clients Database
- **Purpose**: Manages client information and relationships
- **Key Properties**: Client Name, Email, Phone, Website, Project Type, Status
- **Relationship**: Each brand asset can be linked to specific clients

### Projects Database  
- **Purpose**: Main project management and tracking
- **Key Properties**: Project name, Status, Priority, Project Span, Progress
- **Relationship**: Brand assets are associated with specific projects

## Usage Guidelines for Adding New Data

### Required Fields
- **Name** (title): Always required - use descriptive, clear naming
- **Type**: Select appropriate asset type from available options
- **Client**: Link to relevant client if applicable
- **Project**: Link to associated project

### Recommended Fields  
- **Status**: Set appropriate status for tracking
- **Stage**: Indicate current development stage
- **Priority**: Assign priority level for workflow management
- **Client Workflow**: Tag relevant workflow types

### Optional Enhancements
- **Assets**: Upload relevant files
- **Cover**: Add cover image for visual identification
- **Figma Link**: Include design file links
- **Notes**: Add context, instructions, or documentation
- **Asset Template**: Check if this serves as a template

### Workflow Integration
1. **Creation**: Set Name, Type, Client, Project
2. **Planning**: Set Status to "Planning", assign Priority
3. **Development**: Update Stage as work progresses  
4. **Review**: Use Status for review states ("Needs Client Review", etc.)
5. **Completion**: Mark Status as "Complete", set Stage to "Complete"

### Best Practices
- Use consistent naming conventions
- Keep Status and Stage synchronized
- Utilize Client Workflow tags for filtering and reporting
- Upload final assets to Assets property
- Document important decisions in Notes
- Link Figma files for design assets 