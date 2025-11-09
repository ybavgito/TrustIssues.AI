"""Access recommendation tool (least-privilege)"""
from src.models import AccessRecommendation, ToolResult, RiskScore


class AccessRecommender:
    """Recommends least-privilege access levels based on risk"""
    
    def __init__(self):
        self.access_policies = {
            'low': {
                'level': 'standard',
                'permissions': [
                    'view_dashboard',
                    'submit_orders',
                    'view_invoices',
                    'manage_profile',
                    'create_tickets',
                    'upload_documents',
                    'view_reports'
                ],
                'restrictions': [
                    'No financial transaction approval',
                    'No user management',
                    'Rate limited API access'
                ],
                'justification': 'Standard access granted due to low risk profile. Company has been verified and poses minimal security concerns.'
            },
            'medium': {
                'level': 'read_only',
                'permissions': [
                    'view_dashboard',
                    'view_invoices',
                    'view_reports',
                    'view_profile'
                ],
                'restrictions': [
                    'No transaction capabilities',
                    'No document upload',
                    'No user management',
                    'Restricted API access',
                    'Enhanced monitoring enabled'
                ],
                'justification': 'Limited read-only access granted due to medium risk factors. Full access requires additional verification and monitoring period.'
            },
            'high': {
                'level': 'read_only',
                'permissions': [
                    'view_public_info',
                    'view_profile'
                ],
                'restrictions': [
                    'No transaction capabilities',
                    'No document upload',
                    'No sensitive data access',
                    'No API access',
                    'Requires manual approval for each action',
                    'Continuous monitoring enabled'
                ],
                'justification': 'Severely restricted access due to high risk assessment. Full functionality requires successful risk mitigation and enhanced verification.'
            }
        }
    
    def recommend_access(
        self,
        risk_score: RiskScore,
        human_decision: str,
        human_notes: str = None
    ) -> ToolResult:
        """
        Recommend least-privilege access level
        
        Note: This only executes AFTER human approval
        """
        try:
            if human_decision != 'approved':
                return ToolResult(
                    tool_name="recommend_access",
                    success=True,
                    data={
                        'access_level': 'none',
                        'permissions': [],
                        'restrictions': ['Access denied'],
                        'justification': f'Access not granted: {human_decision}'
                    },
                    next_action="complete"
                )
            
            # Get base policy for risk level
            policy = self.access_policies[risk_score.risk_level].copy()
            
            # Adjust based on specific risk factors
            if 'sanctions' in str(risk_score.flags).lower():
                # Sanctions match - maximum restriction
                policy['level'] = 'read_only'
                policy['permissions'] = ['view_public_info']
                policy['restrictions'].append('SANCTIONS ALERT - Requires legal review')
            
            # Add human notes to justification
            if human_notes:
                policy['justification'] += f" Analyst notes: {human_notes}"
            
            recommendation = AccessRecommendation(
                access_level=policy['level'],
                permissions=policy['permissions'],
                restrictions=policy['restrictions'],
                justification=policy['justification']
            )
            
            return ToolResult(
                tool_name="recommend_access",
                success=True,
                data=recommendation.model_dump(),
                next_action="complete"
            )
        
        except Exception as e:
            return ToolResult(
                tool_name="recommend_access",
                success=False,
                error=f"Access recommendation failed: {str(e)}"
            )

