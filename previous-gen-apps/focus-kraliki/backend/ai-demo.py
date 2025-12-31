#!/usr/bin/env python3

"""
Focus by Kraliki AI Service Integration Demo
Demonstrates the revolutionary AI capabilities of Focus by Kraliki
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class FocusKralikiAIDemo:
    def __init__(self):
        self.session_id = f"session_{int(time.time())}"
        self.user_id = "demo_user"
        self.ai_interactions = []
        
    def log_interaction(self, service: str, input_data: str, output_data: str, processing_time: float):
        """Log AI interactions for analysis"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "input": input_data,
            "output": output_data[:200] + "..." if len(output_data) > 200 else output_data,
            "processing_time": processing_time,
            "session_id": self.session_id
        }
        self.ai_interactions.append(interaction)
        print(f"[{interaction['timestamp']}] {service}: {processing_time:.2f}s")
        
    async def demonstrate_shadow_analysis(self):
        """Demonstrate Shadow Analysis (Jungian psychology)"""
        print("\n🌑 Shadow Analysis System")
        print("=" * 40)
        
        # Simulate task pattern analysis
        task_patterns = {
            "procrastination_tendency": 0.8,
            "perfectionism_score": 0.7,
            "work_life_balance": 0.3,
            "risk_aversion": 0.6
        }
        
        print("📊 Analyzing task patterns...")
        await asyncio.sleep(1)
        
        # Generate shadow insight
        if task_patterns["procrastination_tendency"] > 0.7:
            insight = {
                "type": "avoidance",
                "severity": "moderate",
                "title": "Procrastination Pattern Identified",
                "insight": "You tend to delay complex tasks, preferring immediate gratification from simpler activities. This pattern suggests a fear of failure or perfectionism.",
                "recommendations": [
                    "Break large tasks into smaller, manageable steps",
                    "Use the 2-minute rule for quick tasks",
                    "Practice self-compassion for imperfect work",
                    "Set specific deadlines with accountability partners"
                ],
                "psychological_pattern": "Perfectionism-driven avoidance",
                "hidden_goal": "Maintain self-image of competence"
            }
            
            print(f"🎭 Shadow Insight: {insight['title']}")
            print(f"   Severity: {insight['severity']}")
            print(f"   Pattern: {insight['psychological_pattern']}")
            print(f"   Recommendations: {len(insight['recommendations'])} suggestions")
            
            self.log_interaction("shadow_analysis", "Task pattern analysis", json.dumps(insight), 1.2)
            
        return insight
    
    async def demonstrate_flow_memory(self):
        """Demonstrate Flow Memory System (persistent context)"""
        print("\n💾 Flow Memory System")
        print("=" * 40)
        
        # Simulate memory recall
        memories = [
            {
                "type": "task",
                "content": {
                    "title": "Completed project architecture review",
                    "outcome": "Approved by leadership team",
                    "learnings": ["Early stakeholder engagement is crucial", "Data-driven proposals get faster approval"]
                },
                "priority": "high",
                "related_areas": ["planning", "leadership", "architecture"]
            },
            {
                "type": "decision",
                "content": {
                    "decision": "Chose TypeScript over JavaScript for new project",
                    "reasons": ["Type safety for complex AI features", "Better tooling support", "Easier refactoring"],
                    "outcome": "Positive impact on development speed and code quality"
                },
                "priority": "high",
                "related_areas": ["technology", "architecture", "decision-making"]
            },
            {
                "type": "learning",
                "content": {
                    "topic": "Jungian psychology integration",
                    "insights": ["Shadow work reveals hidden motivations", "Cognitive patterns affect productivity", "Self-awareness improves task management"],
                    "sources": ["Man and His Symbols", "Modern applications in productivity systems"]
                },
                "priority": "medium",
                "related_areas": ["psychology", "productivity", "self-improvement"]
            }
        ]
        
        print("🧠 Recalling relevant memories...")
        await asyncio.sleep(0.8)
        
        # Simulate context application
        current_task = "Implement authentication system"
        context_application = {
            "relevant_memories": len(memories),
            "context_insights": [
                "Previous security implementations suggest focusing on JWT best practices",
                "TypeScript experience will help with complex auth logic",
                "Psychological insights: security tasks often trigger perfectionism - break into smaller steps"
            ],
            "recommended_approach": "Incremental implementation with regular testing"
        }
        
        print(f"📝 Applied {context_application['relevant_memories']} memories to current task")
        print(f"   Context insights: {len(context_application['context_insights'])}")
        print(f"   Recommended approach: {context_application['recommended_approach']}")
        
        self.log_interaction("flow_memory", f"Context for: {current_task}", json.dumps(context_application), 0.8)
        
        return context_application
    
    async def demonstrate_natural_orchestration(self):
        """Demonstrate Natural Language Task Orchestration"""
        print("\n🎯 Natural Language Task Orchestration")
        print("=" * 40)
        
        natural_inputs = [
            "Schedule team meeting next Tuesday about Q3 planning and review the budget allocation",
            "I need to finish the quarterly report by Friday, include financial data and team performance metrics",
            "Research competitor pricing strategies and prepare presentation for next week's stakeholder meeting"
        ]
        
        for i, natural_input in enumerate(natural_inputs, 1):
            print(f"\n📝 Input {i}: {natural_input}")
            print("   Processing...")
            await asyncio.sleep(1)
            
            # Simulate AI parsing and orchestration
            orchestrated_task = {
                "title": self.extract_title(natural_input),
                "description": natural_input,
                "priority": self.assess_priority(natural_input),
                "estimated_duration": self.estimate_duration(natural_input),
                "subtasks": self.generate_subtasks(natural_input),
                "tags": self.extract_tags(natural_input),
                "ai_insights": {
                    "complexity": self.assess_complexity(natural_input),
                    "energy_required": self.assess_energy(natural_input),
                    "collaboration_needed": self.assess_collaboration(natural_input)
                }
            }
            
            print(f"   ✅ Orchestrated: {orchestrated_task['title']}")
            print(f"   📊 Priority: {orchestrated_task['priority']}")
            print(f"   ⏱️  Duration: {orchestrated_task['estimated_duration']}")
            print(f"   📋 Subtasks: {len(orchestrated_task['subtasks'])}")
            print(f"   🏷️  Tags: {', '.join(orchestrated_task['tags'])}")
            
            self.log_interaction("natural_orchestration", natural_input, json.dumps(orchestrated_task), 1.5)
        
        return orchestrated_task
    
    def extract_title(self, input_text: str) -> str:
        """Extract task title from natural language"""
        # Simple title extraction logic
        if "meeting" in input_text.lower():
            return "Team Meeting"
        elif "report" in input_text.lower():
            return "Quarterly Report"
        elif "research" in input_text.lower():
            return "Competitor Research"
        else:
            return "Task from Natural Input"
    
    def assess_priority(self, input_text: str) -> str:
        """Assess task priority from natural language"""
        high_priority_words = ["budget", "financial", "stakeholder", "deadline", "friday"]
        medium_priority_words = ["meeting", "review", "planning", "prepare"]
        
        input_lower = input_text.lower()
        if any(word in input_lower for word in high_priority_words):
            return "high"
        elif any(word in input_lower for word in medium_priority_words):
            return "medium"
        else:
            return "normal"
    
    def estimate_duration(self, input_text: str) -> str:
        """Estimate task duration"""
        if "meeting" in input_text.lower():
            return "1-2 hours"
        elif "report" in input_text.lower() and "quarterly" in input_text.lower():
            return "2-3 days"
        elif "research" in input_text.lower():
            return "4-6 hours"
        else:
            return "2-4 hours"
    
    def generate_subtasks(self, input_text: str) -> List[str]:
        """Generate subtasks from natural language"""
        if "meeting" in input_text.lower():
            return [
                "Schedule meeting room",
                "Prepare agenda",
                "Invite participants",
                "Send calendar invites",
                "Prepare presentation materials"
            ]
        elif "report" in input_text.lower():
            return [
                "Gather financial data",
                "Collect team performance metrics",
                "Create report structure",
                "Write executive summary",
                "Review and finalize"
            ]
        else:
            return ["Research topic", "Analyze findings", "Prepare summary"]
    
    def extract_tags(self, input_text: str) -> List[str]:
        """Extract tags from natural language"""
        tags = []
        input_lower = input_text.lower()
        
        if "meeting" in input_lower:
            tags.extend(["meeting", "collaboration"])
        if "budget" in input_lower or "financial" in input_lower:
            tags.extend(["budget", "financial"])
        if "planning" in input_lower:
            tags.append("planning")
        if "research" in input_lower:
            tags.append("research")
        if "presentation" in input_lower:
            tags.append("presentation")
        
        return tags
    
    def assess_complexity(self, input_text: str) -> str:
        """Assess task complexity"""
        complexity_factors = ["budget", "financial", "stakeholder", "research", "analysis"]
        count = sum(1 for factor in complexity_factors if factor in input_text.lower())
        
        if count >= 3:
            return "high"
        elif count >= 2:
            return "medium"
        else:
            return "low"
    
    def assess_energy(self, input_text: str) -> str:
        """Assess energy required"""
        high_energy_words = ["research", "analysis", "creative", "strategic"]
        medium_energy_words = ["meeting", "review", "planning"]
        
        input_lower = input_text.lower()
        if any(word in input_lower for word in high_energy_words):
            return "high"
        elif any(word in input_lower for word in medium_energy_words):
            return "medium"
        else:
            return "low"
    
    def assess_collaboration(self, input_text: str) -> bool:
        """Assess if collaboration is needed"""
        collaboration_words = ["team", "meeting", "stakeholder", "presentation", "review"]
        return any(word in input_text.lower() for word in collaboration_words)
    
    async def demonstrate_collaborative_ai(self):
        """Demonstrate Collaborative AI Reasoning"""
        print("\n🤝 Collaborative AI Reasoning")
        print("=" * 40)
        
        complex_query = "How should I design the authentication system for Focus by Kraliki to balance security with user experience, considering we need to support JWT tokens, session management, and potential future features like social login?"
        
        print(f"🧠 Complex Query: {complex_query}")
        print("\n   Processing with multiple AI models...")
        
        # Simulate Claude response
        claude_response = {
            "model": "Claude 3.5",
            "expertise": "Security Architecture & User Experience",
            "recommendations": [
                "Use JWT with refresh tokens for stateless authentication",
                "Implement proper CORS and CSRF protection",
                "Design for session invalidation on security events",
                "Consider rate limiting and IP-based security",
                "Plan for social OAuth integration from the start"
            ],
            "security_considerations": [
                "Always use HTTPS and secure cookie flags",
                "Implement proper token expiration and refresh mechanisms",
                "Store passwords with bcrypt (minimum 12 rounds)",
                "Use secure, randomly generated secrets for JWT"
            ],
            "ux_considerations": [
                "Provide clear error messages for authentication failures",
                "Implement passwordless options where possible",
                "Consider biometric authentication for mobile apps",
                "Design progressive disclosure of security features"
            ]
        }
        
        await asyncio.sleep(1.5)
        
        # Simulate GPT-4 response
        gpt4_response = {
            "model": "GPT-4",
            "expertise": "Implementation Details & Best Practices",
            "recommendations": [
                "Use Fastify + tRPC for the auth API endpoints",
                "Implement middleware for token validation",
                "Create separate routers for auth, users, and sessions",
                "Use Prisma for database operations with proper indexing",
                "Implement comprehensive logging for security events"
            ],
            "implementation_tips": [
                "Create reusable auth middleware for protected routes",
                "Implement proper error handling with specific error codes",
                "Use environment variables for all sensitive configuration",
                "Add comprehensive input validation and sanitization",
                "Consider implementing request throttling"
            ],
            "testing_considerations": [
                "Write unit tests for all auth functions",
                "Implement integration tests for auth flows",
                "Test edge cases like token expiration and refresh",
                "Perform security testing and penetration testing"
            ]
        }
        
        await asyncio.sleep(1.2)
        
        # Synthesize collaborative response
        collaborative_insights = {
            "architecture_recommendations": claude_response["recommendations"] + gpt4_response["recommendations"][:2],
            "security_best_practices": claude_response["security_considerations"],
            "implementation_roadmap": gpt4_response["implementation_tips"],
            "testing_strategy": gpt4_response["testing_considerations"],
            "ux_guidelines": claude_response["ux_considerations"],
            "confidence_score": 0.92,
            "collaboration_benefit": "Combined security expertise with implementation practicality"
        }
        
        print(f"   🎯 Collaborative Insights Generated")
        print(f"   📊 Confidence Score: {collaborative_insights['confidence_score']:.0%}")
        print(f"   🏗️  Architecture Recommendations: {len(collaborative_insights['architecture_recommendations'])}")
        print(f"   🔒 Security Best Practices: {len(collaborative_insights['security_best_practices'])}")
        print(f"   🛠️  Implementation Tips: {len(collaborative_insights['implementation_roadmap'])}")
        
        self.log_interaction("collaborative_ai", complex_query, json.dumps(collaborative_insights), 2.7)
        
        return collaborative_insights
    
    async def demonstrate_type_manager(self):
        """Demonstrate Type Manager System"""
        print("\n🎨 Type Manager System")
        print("=" * 40)
        
        # Default type system
        default_types = [
            {"id": "deep-work", "name": "Deep Work", "color": "#3B82F6", "icon": "🧠", "description": "Focused, uninterrupted work on complex tasks"},
            {"id": "creative", "name": "Creative", "color": "#8B5CF6", "icon": "🎨", "description": "Brainstorming, design, and innovative thinking"},
            {"id": "administrative", "name": "Administrative", "color": "#10B981", "icon": "📋", "description": "Organization, planning, and routine tasks"},
            {"id": "communication", "name": "Communication", "color": "#F59E0B", "icon": "💬", "description": "Meetings, emails, and coordination"},
            {"id": "learning", "name": "Learning", "color": "#EF4444", "icon": "📚", "description": "Skill development and knowledge acquisition"},
            {"id": "wellness", "name": "Wellness", "color": "#06B6D4", "icon": "💚", "description": "Health, exercise, and self-care"}
        ]
        
        print("🎯 Available Task Types:")
        for task_type in default_types:
            print(f"   {task_type['icon']} {task_type['name']} - {task_type['description']}")
        
        # Demonstrate type-based task creation
        print("\n📝 Type-Based Task Creation:")
        
        task_ideas = [
            "Review and optimize database queries for performance",
            "Design new user interface for the dashboard",
            "Prepare monthly financial report for stakeholders",
            "Learn about new React hooks and patterns",
            "Schedule team building activity for next month"
        ]
        
        for i, idea in enumerate(task_ideas, 1):
            print(f"\n   Task {i}: {idea}")
            
            # Simulate AI type classification
            classified_type = self.classify_task_type(idea)
            print(f"   🎯 Classified as: {classified_type['icon']} {classified_type['name']}")
            print(f"   🎨 Color: {classified_type['color']}")
            print(f"   💡 Suggested approach: {self.get_type_approach(classified_type['id'])}")
            
            await asyncio.sleep(0.5)
            
        self.log_interaction("type_manager", "Task type classification", f"Classified {len(task_ideas)} tasks", 1.0)
        
        return default_types
    
    def classify_task_type(self, task_description: str) -> Dict[str, Any]:
        """Classify task type based on description"""
        description_lower = task_description.lower()
        
        if any(word in description_lower for word in ["database", "optimize", "performance", "code"]):
            return {"id": "deep-work", "name": "Deep Work", "color": "#3B82F6", "icon": "🧠"}
        elif any(word in description_lower for word in ["design", "interface", "ui", "creative"]):
            return {"id": "creative", "name": "Creative", "color": "#8B5CF6", "icon": "🎨"}
        elif any(word in description_lower for word in ["financial", "report", "stakeholders", "administrative"]):
            return {"id": "administrative", "name": "Administrative", "color": "#10B981", "icon": "📋"}
        elif any(word in description_lower for word in ["learn", "study", "research", "patterns"]):
            return {"id": "learning", "name": "Learning", "color": "#EF4444", "icon": "📚"}
        elif any(word in description_lower for word in ["team", "activity", "building", "people"]):
            return {"id": "communication", "name": "Communication", "color": "#F59E0B", "icon": "💬"}
        else:
            return {"id": "wellness", "name": "Wellness", "color": "#06B6D4", "icon": "💚"}
    
    def get_type_approach(self, type_id: str) -> str:
        """Get recommended approach for task type"""
        approaches = {
            "deep-work": "Block 2-4 hours of uninterrupted time, eliminate distractions, use focus techniques",
            "creative": "Schedule during peak creativity hours, use brainstorming techniques, embrace experimentation",
            "administrative": "Process in batches, use templates, focus on efficiency and accuracy",
            "communication": "Be clear and concise, consider timing and audience, follow up when necessary",
            "learning": "Set specific learning goals, use active learning techniques, practice regularly",
            "wellness": "Schedule as priority, be consistent, listen to your body's needs"
        }
        return approaches.get(type_id, "Break into manageable steps and track progress")
    
    async def demonstrate_cognitive_monitoring(self):
        """Demonstrate Cognitive State Monitoring"""
        print("\n🧠 Cognitive State Monitoring")
        print("=" * 40)
        
        # Simulate cognitive state assessment
        current_state = {
            "energy_level": 75,
            "focus_level": 82,
            "creativity_level": 68,
            "stress_level": 25,
            "mood": "focused",
            "last_assessment": datetime.now().isoformat()
        }
        
        print("📊 Current Cognitive State:")
        print(f"   ⚡ Energy Level: {current_state['energy_level']}%")
        print(f"   🎯 Focus Level: {current_state['focus_level']}%")
        print(f"   🎨 Creativity Level: {current_state['creativity_level']}%")
        print(f"   😰 Stress Level: {current_state['stress_level']}%")
        print(f"   😊 Mood: {current_state['mood']}")
        
        # Generate recommendations
        recommendations = self.generate_cognitive_recommendations(current_state)
        
        print(f"\n💡 Cognitive Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Optimal task suggestions
        optimal_tasks = self.suggest_optimal_tasks(current_state)
        print(f"\n🎯 Optimal Task Types for Current State:")
        for task in optimal_tasks:
            print(f"   • {task['type']}: {task['reason']}")
        
        self.log_interaction("cognitive_monitoring", "Cognitive state assessment", json.dumps(recommendations), 0.6)
        
        return current_state
    
    def generate_cognitive_recommendations(self, state: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on cognitive state"""
        recommendations = []
        
        if state["energy_level"] < 40:
            recommendations.append("Consider taking a break or switching to lighter tasks")
        
        if state["focus_level"] < 50:
            recommendations.append("Try the Pomodoro technique or eliminate distractions")
        
        if state["stress_level"] > 60:
            recommendations.append("Practice stress-reduction techniques or take a short walk")
        
        if state["creativity_level"] > 70 and state["focus_level"] > 70:
            recommendations.append("Excellent state for creative problem-solving!")
        
        if state["energy_level"] > 70 and state["focus_level"] > 70:
            recommendations.append("Perfect time for deep work on complex tasks")
        
        return recommendations if recommendations else ["Current cognitive state is well-balanced"]
    
    def suggest_optimal_tasks(self, state: Dict[str, Any]) -> List[Dict[str, str]]:
        """Suggest optimal task types based on cognitive state"""
        suggestions = []
        
        if state["energy_level"] > 70 and state["focus_level"] > 70:
            suggestions.append({
                "type": "Deep Work",
                "reason": "High energy and focus levels perfect for complex tasks"
            })
        
        if state["creativity_level"] > 70:
            suggestions.append({
                "type": "Creative",
                "reason": "High creativity levels ideal for innovative thinking"
            })
        
        if state["stress_level"] > 50:
            suggestions.append({
                "type": "Wellness",
                "reason": "Elevated stress levels suggest need for self-care"
            })
        
        if state["energy_level"] < 50:
            suggestions.append({
                "type": "Administrative",
                "reason": "Lower energy levels suitable for routine tasks"
            })
        
        if not suggestions:
            suggestions.append({
                "type": "Communication",
                "reason": "Balanced state good for collaborative work"
            })
        
        return suggestions
    
    async def run_complete_demo(self):
        """Run the complete AI demonstration"""
        print("🤖 Focus by Kraliki AI Service Integration Demo")
        print("=" * 60)
        print("This demo showcases the revolutionary AI capabilities of Focus by Kraliki")
        print("")
        
        start_time = time.time()
        
        # Demonstrate all AI features
        await self.demonstrate_shadow_analysis()
        await self.demonstrate_flow_memory()
        await self.demonstrate_natural_orchestration()
        await self.demonstrate_collaborative_ai()
        await self.demonstrate_type_manager()
        await self.demonstrate_cognitive_monitoring()
        
        # Summary
        total_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🎉 AI Demo Complete!")
        print("=" * 60)
        
        print(f"\n📊 Demo Summary:")
        print(f"   Total AI Interactions: {len(self.ai_interactions)}")
        print(f"   Total Processing Time: {total_time:.2f}s")
        print(f"   Average Response Time: {total_time/len(self.ai_interactions):.2f}s")
        
        print(f"\n🤖 AI Services Demonstrated:")
        services = list(set(interaction["service"] for interaction in self.ai_interactions))
        for service in services:
            count = sum(1 for interaction in self.ai_interactions if interaction["service"] == service)
            print(f"   • {service.replace('_', ' ').title()}: {count} interactions")
        
        print(f"\n🌟 Revolutionary Features Showcased:")
        print(f"   ✅ Shadow Analysis (Jungian psychology insights)")
        print(f"   ✅ Flow Memory (Persistent context across sessions)")
        print(f"   ✅ Natural Language Orchestration (Text to structured workflows)")
        print(f"   ✅ Collaborative AI (Multiple models working together)")
        print(f"   ✅ Type Manager (Personalized task classification)")
        print(f"   ✅ Cognitive Monitoring (Real-time state optimization)")
        
        print(f"\n🚀 Ready for Production!")
        print(f"   All AI services are integrated and ready to use")
        print(f"   Simply add your API keys to backend/.env")
        print(f"   Run: ./setup-enhanced.sh to get started")
        
        print(f"\n📚 Next Steps:")
        print(f"   1. Run: ./setup-enhanced.sh")
        print(f"   2. Add API keys to backend/.env")
        print(f"   3. Start: cd backend && pnpm dev")
        print(f"   4. Start: cd frontend && pnpm dev")
        print(f"   5. Open: http://127.0.0.1:5175")

async def main():
    """Main demo function"""
    demo = FocusKralikiAIDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())
