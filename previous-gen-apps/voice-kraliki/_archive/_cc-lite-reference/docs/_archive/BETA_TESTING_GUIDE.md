# Voice by Kraliki Beta Testing Guide

## 🎯 Welcome Beta Testers!

Thank you for participating in Voice by Kraliki's beta testing program. Your feedback is crucial for improving the platform.

## 🔑 Getting Started

### 1. Access the Platform

**Beta URL**: `https://beta.cc-lite.yourdomain.com`

### 2. Test Accounts

You will receive your test credentials via email:
- Email: `your-email@domain.com`
- Password: `[Provided separately]`

**Test Roles Available**:
- **Agent**: Call handling and customer interaction
- **Supervisor**: Team management and monitoring
- **Admin**: Full system access

### 3. First Login

1. Navigate to `https://beta.cc-lite.yourdomain.com`
2. Click "Login"
3. Enter your credentials
4. Complete profile setup

## 🧪 What to Test

### Core Features

#### 1. Authentication & User Management
- [ ] Login with provided credentials
- [ ] Change password
- [ ] Update profile information
- [ ] Session persistence
- [ ] Logout functionality

#### 2. Dashboard (All Roles)
- [ ] Dashboard loads without errors
- [ ] Real-time metrics update
- [ ] Responsive design on mobile/tablet
- [ ] Dark mode toggle works
- [ ] Navigation menu functions

#### 3. Agent Dashboard
- [ ] View active call queue
- [ ] Access call history
- [ ] Use quick actions panel
- [ ] View performance metrics
- [ ] Access knowledge base
- [ ] Customer sentiment indicators

#### 4. Supervisor Dashboard
- [ ] Monitor active calls
- [ ] View live transcriptions
- [ ] Manage call queues
- [ ] View team performance
- [ ] Access real-time analytics
- [ ] Agent status monitoring

#### 5. Call Center Features
- [ ] Make outbound calls (if telephony configured)
- [ ] Receive inbound calls
- [ ] Transfer calls
- [ ] Put calls on hold
- [ ] Call recording
- [ ] Real-time transcription
- [ ] Sentiment analysis

#### 6. Campaign Management
- [ ] Create new campaigns
- [ ] Import contact lists (CSV)
- [ ] Configure campaign settings
- [ ] Start/stop campaigns
- [ ] View campaign analytics
- [ ] Export campaign results

#### 7. Analytics & Reporting
- [ ] View call volume charts
- [ ] Generate performance reports
- [ ] Export data to CSV/PDF
- [ ] Real-time sentiment dashboard
- [ ] Agent performance metrics

#### 8. Settings & Configuration
- [ ] Update notification preferences
- [ ] Configure telephony settings
- [ ] Manage team members
- [ ] Set working hours
- [ ] Customize interface

## 🐛 Bug Reporting

### How to Report Bugs

Voice by Kraliki includes a built-in bug reporting system:

1. **Click the Bug Report Button** (bottom-right corner)
2. **Fill out the form**:
   - **Title**: Brief description of the issue
   - **Description**: Detailed explanation
   - **Steps to Reproduce**: How to recreate the bug
   - **Expected Behavior**: What should happen
   - **Actual Behavior**: What actually happens
   - **Severity**: Critical / High / Medium / Low
3. **Attach Screenshots** (if applicable)
4. **Submit**

Your bug report will automatically create a ticket in our issue tracker.

### Bug Severity Guidelines

- **Critical**: System crashes, data loss, security issues
- **High**: Major features broken, workaround difficult
- **Medium**: Features partially working, workaround available
- **Low**: Cosmetic issues, minor inconveniences

### What to Include in Bug Reports

✅ **Good Bug Report**:
```
Title: Unable to transfer calls to supervisor

Steps to Reproduce:
1. Login as agent
2. Answer incoming call
3. Click "Transfer" button
4. Select supervisor from list
5. Click "Confirm Transfer"

Expected: Call should transfer to supervisor
Actual: Error message "Transfer failed" appears

Browser: Chrome 121.0.0
Device: Desktop Windows 11
Severity: High
```

❌ **Bad Bug Report**:
```
Title: Calls don't work

Description: I tried to make a call and it didn't work.
```

## 💡 Feature Requests

### Submit Suggestions

Use the bug report system for feature requests:
- Set severity to "Low"
- Start title with "[FEATURE]"
- Explain the use case and benefits

**Example**:
```
Title: [FEATURE] Add bulk SMS notification

Description:
As a supervisor, I want to send bulk SMS notifications to my team
for urgent updates, so that I can quickly communicate important
information without calling everyone individually.

Benefit: Faster team communication during emergencies
```

## 📊 Testing Scenarios

### Scenario 1: Agent Workflow
1. Login as agent
2. Set status to "Available"
3. Wait for/initiate call
4. Use AI assist during call
5. Add call notes
6. Complete call disposition
7. Review call recording

### Scenario 2: Supervisor Monitoring
1. Login as supervisor
2. View active calls dashboard
3. Monitor live transcriptions
4. Check sentiment analysis
5. Access agent performance metrics
6. Export daily report

### Scenario 3: Campaign Management
1. Login as admin
2. Create new outbound campaign
3. Upload contact list (CSV)
4. Configure campaign settings
5. Assign agents
6. Start campaign
7. Monitor progress
8. Generate campaign report

### Scenario 4: Multi-Language Support
1. Initiate call in Spanish
2. Verify automatic language detection
3. Check transcript accuracy
4. Test TTS in Czech language
5. Validate sentiment analysis

### Scenario 5: Mobile Experience
1. Access platform on mobile device
2. Test all core features
3. Check responsive design
4. Verify touch interactions
5. Test mobile notifications

## 🔍 What We're Looking For

### Performance
- Page load times
- Response times for actions
- Real-time update latency
- Memory usage
- Battery drain (mobile)

### Usability
- Intuitive navigation
- Clear labels and instructions
- Accessible design
- Error message clarity
- Help documentation

### Reliability
- System stability
- Error handling
- Data persistence
- Session management
- Backup/recovery

### Security
- Unauthorized access attempts
- Data leakage
- XSS vulnerabilities
- CSRF protection
- Session hijacking

## 📅 Testing Timeline

**Beta Phase 1** (Weeks 1-2):
- Core functionality testing
- Critical bug identification
- Performance baseline

**Beta Phase 2** (Weeks 3-4):
- Advanced features testing
- Integration testing
- Load testing

**Beta Phase 3** (Weeks 5-6):
- Polish and refinement
- Documentation review
- Final bug fixes

## 🏆 Beta Tester Benefits

- **Early Access**: Be the first to use new features
- **Direct Influence**: Your feedback shapes the product
- **Recognition**: Listed in credits (optional)
- **Exclusive Perks**: Discounted pricing at launch

## 📞 Support Channels

### Technical Issues
- **Bug Reports**: Use in-app bug reporter
- **Email**: beta-support@yourdomain.com
- **Response Time**: Within 24 hours

### Questions & Feedback
- **Email**: feedback@yourdomain.com
- **Forum**: [Beta Tester Forum URL]
- **Slack**: [Beta Tester Slack Invite]

### Emergency Contact
For critical security issues:
- **Email**: security@yourdomain.com
- **Priority**: Immediate response

## 📋 Testing Checklist

### Week 1-2
- [ ] Complete initial login and setup
- [ ] Test core dashboard features
- [ ] Submit at least 3 bug reports
- [ ] Complete 5 test calls
- [ ] Review documentation

### Week 3-4
- [ ] Test advanced features
- [ ] Try mobile interface
- [ ] Test different browsers
- [ ] Submit feature requests
- [ ] Participate in feedback session

### Week 5-6
- [ ] Re-test fixed bugs
- [ ] Verify improvements
- [ ] Complete final survey
- [ ] Document overall experience

## 🎖️ Testing Best Practices

1. **Test Regularly**: Use the system daily if possible
2. **Be Thorough**: Don't just test happy paths
3. **Document Everything**: Screenshots help immensely
4. **Be Specific**: Detailed reports are more valuable
5. **Test Edge Cases**: Try unusual inputs and scenarios
6. **Check Different Devices**: Desktop, mobile, tablet
7. **Try Different Browsers**: Chrome, Firefox, Safari, Edge

## 🔒 Confidentiality Agreement

Beta testers must agree to:
- Keep all information confidential
- Not share credentials with others
- Not take screenshots containing sensitive data
- Report security vulnerabilities privately
- Comply with terms of service

## 📊 Feedback Survey

At the end of the beta period, complete our survey:
- Overall satisfaction rating
- Feature usefulness ratings
- Performance evaluation
- Suggested improvements
- Would you recommend Voice by Kraliki?

## 🙏 Thank You!

Your participation in this beta program is invaluable. Every bug report, feature suggestion, and piece of feedback helps us build a better product.

---

**Questions?** Contact us at beta-support@yourdomain.com

**Happy Testing! 🚀**