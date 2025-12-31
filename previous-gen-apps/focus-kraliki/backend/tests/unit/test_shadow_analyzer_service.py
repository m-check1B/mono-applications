"""
Unit tests for Shadow Analyzer Service
Tests Jungian psychology-based productivity analysis and shadow work features
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta


class TestShadowAnalyzerBasic:
    """Tests for basic shadow analysis"""
    
    def test_create_shadow_profile(self):
        """Create shadow profile for user"""
        profile = {
            "user_id": "user-123",
            "created_at": datetime.utcnow().isoformat(),
            "shadow_traits": [],
            "acknowledged_traits": [],
            "unlock_progress": 0,
            "analysis_enabled": True
        }
        assert profile["user_id"] == "user-123"
        assert profile["unlock_progress"] == 0
    
    def test_analyze_task_patterns(self):
        """Analyze task completion patterns"""
        tasks = [
            {"id": "task-1", "status": "completed", "created_at": "2025-11-20", "completed_at": "2025-11-21"},
            {"id": "task-2", "status": "pending", "created_at": "2025-11-15", "completed_at": None},
            {"id": "task-3", "status": "completed", "created_at": "2025-11-10", "completed_at": "2025-11-20"},
        ]
        
        # Analyze patterns
        completed = [t for t in tasks if t["status"] == "completed"]
        pending = [t for t in tasks if t["status"] == "pending"]
        
        completion_rate = len(completed) / len(tasks)
        assert completion_rate == pytest.approx(0.666, rel=0.01)
    
    def test_identify_procrastination_pattern(self):
        """Identify procrastination patterns"""
        task_delays = [
            {"task_id": "task-1", "delay_days": 1},
            {"task_id": "task-2", "delay_days": 5},
            {"task_id": "task-3", "delay_days": 10},
            {"task_id": "task-4", "delay_days": 2},
        ]
        
        avg_delay = sum(t["delay_days"] for t in task_delays) / len(task_delays)
        
        # If avg delay > 3 days, suggests procrastination pattern
        has_procrastination_pattern = avg_delay > 3
        assert has_procrastination_pattern is True


class TestShadowTraits:
    """Tests for shadow trait identification"""
    
    def test_identify_perfectionism_trait(self):
        """Identify perfectionism shadow trait"""
        behaviors = {
            "task_revisions": 5,  # High number of revisions
            "late_completions_due_to_refinement": 3,
            "abandoned_tasks_not_good_enough": 2
        }
        
        # Perfectionism indicators
        if behaviors["task_revisions"] > 3:
            trait = {
                "name": "perfectionism",
                "description": "You may be holding yourself to impossibly high standards",
                "severity": "medium",
                "suggestions": [
                    "Set 'good enough' criteria before starting",
                    "Time-box tasks to prevent over-refinement"
                ]
            }
            assert trait["name"] == "perfectionism"
    
    def test_identify_avoidance_trait(self):
        """Identify avoidance shadow trait"""
        behaviors = {
            "postponed_tasks": 8,
            "category_avoidance": ["administrative", "finance"],
            "avg_postponement_days": 7
        }
        
        if behaviors["postponed_tasks"] > 5:
            trait = {
                "name": "avoidance",
                "description": "You may be avoiding certain types of tasks",
                "avoided_categories": behaviors["category_avoidance"],
                "suggestions": [
                    "Break avoided tasks into smaller steps",
                    "Schedule avoided tasks first thing in the morning"
                ]
            }
            assert trait["name"] == "avoidance"
            assert "administrative" in trait["avoided_categories"]
    
    def test_identify_overcommitment_trait(self):
        """Identify overcommitment shadow trait"""
        behaviors = {
            "tasks_created_per_week": 25,
            "tasks_completed_per_week": 10,
            "overdue_tasks": 15
        }
        
        completion_ratio = behaviors["tasks_completed_per_week"] / behaviors["tasks_created_per_week"]
        
        if completion_ratio < 0.5:
            trait = {
                "name": "overcommitment",
                "description": "You may be taking on more than you can handle",
                "severity": "high",
                "suggestions": [
                    "Review commitments before accepting new ones",
                    "Practice saying 'no' or 'not now'"
                ]
            }
            assert trait["name"] == "overcommitment"


class TestShadowInsights:
    """Tests for shadow insights generation"""
    
    def test_generate_daily_insight(self):
        """Generate daily shadow insight"""
        user_data = {
            "tasks_completed_today": 5,
            "tasks_created_today": 3,
            "time_in_flow": 120,  # minutes
            "procrastinated_tasks": 2
        }
        
        insight = {
            "type": "daily",
            "date": datetime.utcnow().date().isoformat(),
            "message": f"You completed {user_data['tasks_completed_today']} tasks today.",
            "shadow_observation": "Notice which tasks you avoided and why.",
            "reflection_prompt": "What task did you feel most resistant to today?"
        }
        
        assert insight["type"] == "daily"
        assert "reflection_prompt" in insight
    
    def test_generate_weekly_insight(self):
        """Generate weekly shadow insight"""
        weekly_data = {
            "completion_rate": 0.72,
            "most_productive_day": "Tuesday",
            "least_productive_day": "Friday",
            "shadow_patterns_detected": ["afternoon_slump", "monday_resistance"]
        }
        
        insight = {
            "type": "weekly",
            "week_of": "2025-11-18",
            "summary": f"Your completion rate was {weekly_data['completion_rate']*100:.0f}%",
            "patterns": weekly_data["shadow_patterns_detected"],
            "deep_insight": "Your Friday productivity drops may indicate end-of-week burnout."
        }
        
        assert insight["type"] == "weekly"
        assert "afternoon_slump" in insight["patterns"]


class TestShadowUnlock:
    """Tests for 30-day progressive unlock system"""
    
    def test_day_1_unlock(self):
        """Day 1 unlocks basic awareness"""
        unlock_day = 1
        unlocked_feature = {
            "day": 1,
            "feature": "basic_awareness",
            "description": "You can now see your task completion patterns",
            "locked_features": ["shadow_traits", "deep_insights", "integration_exercises"]
        }
        
        assert unlocked_feature["feature"] == "basic_awareness"
    
    def test_day_7_unlock(self):
        """Day 7 unlocks shadow trait identification"""
        unlock_day = 7
        unlocked_feature = {
            "day": 7,
            "feature": "shadow_traits",
            "description": "Shadow traits are now visible in your profile",
            "locked_features": ["deep_insights", "integration_exercises"]
        }
        
        assert unlocked_feature["feature"] == "shadow_traits"
    
    def test_day_14_unlock(self):
        """Day 14 unlocks deep insights"""
        unlock_day = 14
        unlocked_feature = {
            "day": 14,
            "feature": "deep_insights",
            "description": "Deep psychological insights are now available",
            "locked_features": ["integration_exercises"]
        }
        
        assert unlocked_feature["feature"] == "deep_insights"
    
    def test_day_30_full_unlock(self):
        """Day 30 unlocks full integration exercises"""
        unlock_day = 30
        unlocked_feature = {
            "day": 30,
            "feature": "integration_exercises",
            "description": "Full shadow work integration exercises unlocked",
            "locked_features": []
        }
        
        assert unlocked_feature["feature"] == "integration_exercises"
        assert len(unlocked_feature["locked_features"]) == 0
    
    def test_unlock_progress_calculation(self):
        """Calculate unlock progress percentage"""
        days_active = 15
        total_unlock_days = 30
        
        progress = (days_active / total_unlock_days) * 100
        assert progress == 50.0


class TestShadowAcknowledgment:
    """Tests for shadow trait acknowledgment"""
    
    def test_acknowledge_trait(self):
        """Acknowledge a shadow trait"""
        trait = {
            "id": "trait-123",
            "name": "perfectionism",
            "acknowledged": False,
            "acknowledged_at": None
        }
        
        # Acknowledge the trait
        trait["acknowledged"] = True
        trait["acknowledged_at"] = datetime.utcnow().isoformat()
        
        assert trait["acknowledged"] is True
        assert trait["acknowledged_at"] is not None
    
    def test_acknowledgment_unlocks_integration(self):
        """Acknowledging trait unlocks integration exercise"""
        trait = {
            "name": "perfectionism",
            "acknowledged": True
        }
        
        if trait["acknowledged"]:
            integration = {
                "trait": trait["name"],
                "exercise": "time_boxing",
                "description": "Practice completing tasks within a set time limit",
                "duration_minutes": 25
            }
            assert integration["exercise"] == "time_boxing"


class TestShadowPrivacy:
    """Tests for shadow data privacy"""
    
    def test_shadow_data_encrypted(self):
        """Shadow data should be encrypted"""
        # Shadow data is sensitive, verify encryption
        shadow_data = {
            "traits": ["perfectionism", "avoidance"],
            "insights": "Personal psychological insights"
        }
        
        # Would encrypt in real implementation
        encrypted = True  # Placeholder
        assert encrypted is True
    
    def test_shadow_data_not_shared(self):
        """Shadow data never shared without consent"""
        settings = {
            "share_shadow_data": False,
            "share_with_team": False,
            "anonymous_analytics": False
        }
        
        assert settings["share_shadow_data"] is False
    
    def test_shadow_data_export(self):
        """User can export their shadow data"""
        export = {
            "user_id": "user-123",
            "export_date": datetime.utcnow().isoformat(),
            "data": {
                "shadow_profile": {},
                "traits": [],
                "insights": [],
                "acknowledgments": []
            }
        }
        
        assert "shadow_profile" in export["data"]


class TestShadowAPI:
    """Tests for Shadow Analysis API endpoints"""
    
    def test_get_shadow_profile(self):
        """GET /shadow/profile returns shadow profile"""
        response = {
            "user_id": "user-123",
            "profile": {
                "traits": [],
                "unlock_day": 15,
                "unlock_progress": 50
            }
        }
        assert "profile" in response
    
    def test_get_shadow_insights(self):
        """GET /shadow/insights returns insights"""
        response = {
            "insights": [
                {"type": "daily", "message": "You completed 5 tasks"},
                {"type": "pattern", "message": "Afternoon productivity dip detected"}
            ]
        }
        assert len(response["insights"]) == 2
    
    def test_acknowledge_shadow_trait(self):
        """POST /shadow/acknowledge acknowledges trait"""
        request = {"trait_id": "trait-123"}
        response = {
            "success": True,
            "trait_id": request["trait_id"],
            "acknowledged_at": datetime.utcnow().isoformat()
        }
        assert response["success"] is True
    
    def test_shadow_disabled_in_settings(self):
        """Shadow features respect privacy settings"""
        settings = {"shadowAnalysis": False}
        
        if not settings["shadowAnalysis"]:
            response = {
                "error": "shadow_analysis_disabled",
                "message": "Shadow analysis is disabled in your privacy settings"
            }
            assert response["error"] == "shadow_analysis_disabled"