# Hospital Managment System Casestudy

## TODOs
- [x] Create users DB
- [x] Create patients DB
     - [x] Create Patient Screen
     - [x] Update Patient Screen
     - [x] Delete Patient Screen
     - [x] Search Patient Screen
     - [x] View Patients Screen
     - [x] Patient Billing Screen
- [x] login page (basic)
- [x] added authentication
- [x] cookies
- [x] UI Enhancement
     - [ ] Home Page
     - [x] Login Page
     - [x] Navbar
- [x] create medicines DB
     - [x] Get patient Details Screen
     - [x] Issue Medicines Screen
- [x] create diagnostics DB
     - [x] Get patient Details Screen 
     - [x] Diagnostics Screen

## Login Credentials:
__`Username:`__ reuser1  
__`Password:`__ tcs_user1

## Database Schemas
* patients Table
  ```
          col name    | type    | remarks
          -------------------------------------------
          ws_ssn      | INTEGER | UNIQUE values only
		ws_pat_id   | INTEGER | PRIMARY KEY, AUTOINCREMENT
		ws_pat_name | TEXT    | NOT NULL
		ws_adrs     | TEXT    | NOT NULL
		ws_age      | INTEGER | NOT NULL
		ws_doj      | TEXT    | NOT NULL
		ws_rtype    | TEXT    |   - 
		ws_status   | INTEGER | DEFAULT value 1
  ```
* users Table
  ```
       col name     | type    | remarks
       --------------------------------------
       id           | TEXT    | PRIMARY KEY
       name         | TEXT    | NOT NULL
       password     | TEXT    | NOT NULL, SHA256 encrypted
       type         | TEXT    | NOT NULL
  ```
