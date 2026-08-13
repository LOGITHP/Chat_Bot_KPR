from typing import Dict, Any, List, Optional
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
from app.vector.qdrant_client import qdrant_client

def build_auth_filter(user_profile: dict, is_guest: bool = False, requested_scope: dict = None) -> Filter:
    """
    Builds a Qdrant Filter based on user authorization and requested scope.
    requested_scope can have keys like 'department_id', 'club_id', 'category_id'.
    """
    must_conditions = [
        FieldCondition(key="active", match=MatchValue(value=True))
    ]
    
    if is_guest:
        # Guests can only access public documents
        must_conditions.append(FieldCondition(key="access_level", match=MatchValue(value="public")))
    else:
        role = user_profile.get("role", "student")
        
        if role != "admin":
            should_conditions = [
                FieldCondition(key="access_level", match=MatchValue(value="public")),
                FieldCondition(key="access_level", match=MatchValue(value="students"))
            ]
            
            if role == "faculty":
                should_conditions.append(FieldCondition(key="access_level", match=MatchValue(value="faculty")))
            
            # Department access
            user_dept = user_profile.get("department_id")
            if user_dept:
                should_conditions.append(
                    Filter(
                        must=[
                            FieldCondition(key="access_level", match=MatchValue(value="department")),
                            FieldCondition(key="department_id", match=MatchValue(value=user_dept))
                        ]
                    )
                )
                
            # Club access
            user_clubs = user_profile.get("club_ids", [])
            if user_clubs:
                should_conditions.append(
                    Filter(
                        must=[
                            FieldCondition(key="access_level", match=MatchValue(value="club")),
                            FieldCondition(key="club_id", match=MatchAny(any=user_clubs))
                        ]
                    )
                )
            
            must_conditions.append(Filter(should=should_conditions))
            
    # Apply requested scope (which can only narrow the authorization)
    if requested_scope:
        if requested_scope.get("department_id"):
            must_conditions.append(FieldCondition(key="department_id", match=MatchValue(value=requested_scope["department_id"])))
        if requested_scope.get("club_id"):
            must_conditions.append(FieldCondition(key="club_id", match=MatchValue(value=requested_scope["club_id"])))
        if requested_scope.get("category_id"):
            must_conditions.append(FieldCondition(key="category_id", match=MatchValue(value=requested_scope["category_id"])))

    return Filter(must=must_conditions)

def retrieve_context(query: str, user_profile: dict, is_guest: bool = False, requested_scope: dict = None, top_k: int = 5) -> List[Dict[str, Any]]:
    auth_filter = build_auth_filter(user_profile, is_guest, requested_scope)
    return qdrant_client.search(query, filters=auth_filter, top_k=top_k)
