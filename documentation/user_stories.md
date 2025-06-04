# LNHM Plant Monitoring - User Stories

## Story 1: Automated Plant Health Data Collection
**As a** museum system administrator  
**I want** plant sensor data to be automatically collected every minute from all 50 plants  
**So that** all plants can be monitored without manual intervention

**Acceptance Criteria:**
- All plant readings are collected every minute
- System logs successful/failed collections
- Pipeline continues if some plant readings contain errors or sensors are offline


## Story 2: Plant Health Alerts
**As a** botanist responsible for plant's care  
**I want** to receive email/sms alerts when any plant's soil moisture drops below 30%  
**So that** I can water plants before they become stressed or perish  

**Acceptance Criteria:**
- Email/sms sent to botanist when soil moisture <= 30%
- Alert includes plant name, current moisture level, and botanist contact
- Alert sent within 5 minutes of detection
- No duplicated alerts for same plant within 2 hours(?)

------

## Story 3: Plant Health Short-Term Data Storage
**As a** Exhibitions manager  
**I want** the past 24 hours of plant readings stored in an accessible database  
**So that** staff can review recent plant health trends 

**As a** botanical researcher
**I want** to be notified if my plants are under environmental stress
**So that** I can tailor the conditions to keep my plants remain healthy  

**Acceptance Criteria:**
- All plant readings stored in database
- Data includes all relevant fields from API response 
- Readings older than 24 hours are automatically removed and archived
- Database queries return results in under 2 seconds
---

## Story 4: Plant Health Long-Term Data Storage
**As a** botanical researcher  
**I want** daily plant health summaries archived for historical analysis  
**So that** I can study long-term trends and seasonal patterns 

**As the** Head of visitor safety
**I want** to monitor temperatures of the greenhouse over time
**So that** I can ensure that the temperature remains within museum regulations

**Acceptance Criteria:**
- Daily summaries created with min/max/avg temperatures and moisture per plant
- Summaries stored in cost-effective cloud storage (S3)
- Archive process runs automatically each evening.
---

## Story 5: Plant Health Real-Time Dashboard
**As a** head gardener  
**I want** to see current status of all plants on a single dashboard  
**So that** I can quickly identify which plants need immediate attention  

**Acceptance Criteria:**
- Dashboard shows current temperature and moisture for all plants
- Utilise Color coding: Green (healthy), Yellow (warning), Red (critical)
- Updates automatically every minute

---
