# Demo Improvements Context

## 1. Current System State

### Architecture Overview
- **Backend**: FastAPI with Neo4j memory graph + Claude 4 AI
- **Frontend**: React with TypeScript 
- **AI Persona**: Sage (therapeutic conversations)
- **Memory System**: Intelligent storage of moments, emotions, patterns, values, contradictions

### Current User Management
- **User ID Generation**: `user_${Date.now()}_${randomString}` (e.g., `user_1751884198048_s55wqudqn`)
- **Database Schema**: User nodes with `user_id` and `name` fields
- **Current Display**: Showing last 8 characters of user_id when name is null
- **Problem**: Ugly technical IDs visible in demo interface

### Services Status
- ✅ Neo4j: Running on localhost:7687
- ✅ Backend: FastAPI on localhost:8000  
- ✅ Frontend: React dev server on localhost:5173
- ✅ Memory System: Fully functional with high-quality storage

## 2. Problem Definition

### What Needs to Change
[Describe the specific issues with current user naming system]

### Demo Impact
[Explain how ugly user IDs affect demo experience]

### User Experience Goals
[Define what the ideal user experience should look like]

## 3. Desired Outcome

### User Interface
[Describe how users should be displayed in the frontend]

### Database Structure
[Define how user data should be stored]

### Naming System
[Specify the friendly naming approach]

### User Management
[Explain how multiple users should work]

## 4. Implementation Approach

### Phase 1: User Name Generation
[Define how friendly names will be created]

### Phase 2: Database Migration
[Outline how existing data will be handled]

### Phase 3: Frontend Updates
[List UI changes needed]

### Phase 4: Testing & Cleanup
[Define validation and cleanup steps]

## 5. Technical Constraints

### Must Preserve
[List what cannot be changed/broken]

### Database Considerations
[Note any Neo4j-specific requirements]

### API Compatibility
[Define any API contract requirements]

## 6. Success Criteria

### Demo Experience
[Define what makes a successful demo]

### Technical Validation
[List how to verify the changes work]

### Cleanup Requirements
[Note any cleanup/reset needs] 