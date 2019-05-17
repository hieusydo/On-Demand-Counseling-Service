# On-Demand Counseling Service

## Features
- [ ] Sign-in and dashboard page for user
- [ ] Sign-in and dashboard page for counselor
- [ ] NoSQL: available counselors
- [ ] DynamoDB: counselors info
- [ ] DynamoDB: student info
- [ ] DynamoDB: counselors info
- [ ] Lambda: handle chat
- [ ] Elasticsearch domain for the articles

elasticsearch domain: available counselors
    counselorId
    status: Online, InSession, Offline

DynamoDB
    Counselor:
        info
        sessionId

    Session
        sessionId
        time

    User
        info
        sessionId


https://heka-student.auth.us-east-1.amazoncognito.com/login?response_type=token&client_id=70nasoc4kjsjnllrfkg5f3oivh&redirect_uri=https://s3.amazonaws.com/nyu-heka/student/student.html

https://heka-counselor.auth.us-east-1.amazoncognito.com/login?response_type=token&client_id=3rvc37il8j7fffsgv73fc2jsvo&redirect_uri=https://s3.amazonaws.com/nyu-heka/counselor/counselor.html