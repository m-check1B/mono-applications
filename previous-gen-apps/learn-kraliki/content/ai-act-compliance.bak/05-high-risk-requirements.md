# High-Risk AI Requirements

## Overview

High-risk AI systems face **strict compliance requirements**. This module covers the 10 mandatory requirements and how to implement them.

## The 10 Mandatory Requirements

### 1. Risk Management System

**Requirement:** Continuous risk identification, assessment, and mitigation

**What You Need:**
- [ ] Documented risk management process
- [ ] Risk identification for AI system lifecycle
- [ ] Risk assessment (likelihood × impact)
- [ ] Mitigation strategies for each risk
- [ ] Regular risk reviews

**Implementation:**
```markdown
## Risk Management Framework

1. Identify risks across lifecycle:
   - Data collection and processing
   - Model development and training
   - Deployment and monitoring
   - Updates and maintenance

2. Assess each risk:
   - Severity: Low / Medium / High / Critical
   - Likelihood: Rare / Unlikely / Possible / Likely
   - Impact: On health, safety, fundamental rights

3. Mitigate high/critical risks:
   - Implement technical controls
   - Add human oversight
   - Create fallback procedures
   - Document mitigation steps
```

### 2. High-Quality Training Data

**Requirement:** Data must be relevant, representative, and free from errors

**What You Need:**
- [ ] Data quality assessment
- [ ] Bias detection and mitigation
- [ ] Data governance procedures
- [ ] Documentation of data sources

**Data Quality Checklist:**
- ✅ Relevant to intended purpose
- ✅ Representative of target population
- ✅ Free from systematic errors
- ✅ Properly labeled/annotated
- ✅ Documented provenance
- ✅ Legal basis for use (GDPR compliance)

**Bias Mitigation:**
- Test for disparate impact
- Oversample underrepresented groups
- Use fairness-aware algorithms
- Regular bias audits
- Document bias detection process

### 3. Technical Documentation

**Requirement:** Comprehensive documentation for conformity assessment

**Required Documents:**
1. **General System Information**
   - System name, purpose, intended use
   - Provider information
   - Conformity assessment procedures

2. **System Description**
   - System architecture
   - Data flow diagrams
   - Key components and interactions

3. **Risk Assessment**
   - Identified risks and mitigations
   - Safety measures
   - Test results

4. **Quality Management**
   - Procedures used during development
   - Validation protocols
   - Performance metrics

5. **Instructions for Use**
   - Intended use cases
   - Limitations and restrictions
   - Performance characteristics

6. **Monitoring Mechanisms**
   - Post-market monitoring plan
   - Update procedures
   - Incident response

### 4. Record-Keeping

**Requirement:** Automatic logging of AI system operations

**What to Log:**
- [ ] System inputs and outputs
- [ ] Timestamps of all operations
- [ ] User identification
- [ ] Decision outcomes
- [ ] System version information
- [ ] Errors and exceptions

**Retention Period:** **Minimum 10 years**

### 5. Transparency & User Information

**Requirement:** Clear, understandable information to deployers

**Information Must Include:**
- System purpose and intended use
- Level of accuracy and robustness
- Known limitations
- Human oversight mechanisms
- Monitoring and update procedures

**For End Users:**
- Clear indication of AI interaction
- Ability to contest decisions
- Human contact for review
- Explanation of decision (when feasible)

### 6. Human Oversight

**Requirement:** Meaningful human control over AI system

**Implementation Requirements:**
- [ ] Human in the loop for critical decisions
- [ ] Override mechanisms for AI decisions
- [ ] Human review periods
- [ ] Training for human operators
- [ ] Clear accountability structure

**Oversight Levels:**
| Risk Level | Oversight Type |
|------------|----------------|
| Critical | Human in loop for every decision |
| High | Human review of critical decisions |
| Medium | Human override available |
| Low | Periodic human review |

### 7. Accuracy, Robustness, Cybersecurity

**Requirement:** System performs reliably and securely

**Accuracy:**
- [ ] Validated against ground truth
- [ ] Confidence scores for predictions
- [ ] Known error rates
- [ ] Regular accuracy monitoring

**Robustness:**
- [ ] Handles edge cases
- [ ] Resistant to adversarial attacks
- [ ] Graceful degradation on errors
- [ ] Performance across diverse conditions

**Cybersecurity:**
- [ ] Secure data handling
- [ ] Protection against manipulation
- [ ] Access controls
- [ ] Regular security audits
- [ ] Incident response procedures

### 8. Conformity Assessment

**Requirement:** Third-party certification before deployment

**Process:**
1. **Self-Assessment** - Internal review against requirements
2. **Third-Party Assessment** - Independent notified body review
3. **Declaration of Conformity** - Official document
4. **CE Marking** - EU compliance indicator

**Who Does Assessment:**
- Notified Bodies (independent organizations)
- Authorized by national authorities
- Sector-specific expertise
- Recognized across EU

### 9. Quality Management System

**Requirement:** Systematic quality processes throughout lifecycle

**QMS Components:**
- [ ] Quality policy and objectives
- [ ] Development procedures
- [ ] Testing protocols
- [ ] Document control
- [ ] Supplier management
- [ ] Continuous improvement

**Standards:**
- ISO 9001 (Quality Management)
- ISO/IEC 27001 (Information Security)
- Industry-specific standards

### 10. Post-Market Monitoring

**Requirement:** Ongoing monitoring after deployment

**Monitoring Activities:**
- [ ] Performance metrics tracking
- [ ] User feedback collection
- [ ] Incident reporting
- [ ] Regular system audits
- [ ] Reassessment of risks

**Incident Response:**
- Immediate reporting of serious incidents
- Root cause analysis
- Corrective actions
- Notification to authorities (within 48 hours for serious incidents)

## Implementation Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| **Planning** | 1-2 months | Gap analysis, roadmap creation |
| **Documentation** | 2-4 months | Create technical documentation |
| **Controls** | 3-6 months | Implement all controls |
| **Testing** | 1-2 months | Validation and verification |
| **Assessment** | 1-2 months | Third-party conformity assessment |
| **Total** | 8-16 months | Full compliance journey |

---

**Next Lesson:** Transparency Obligations
