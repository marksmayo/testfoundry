"""
Advanced validation utilities for configuration.
Provides URL validation, project name sanitization, etc.
"""

import re
import urllib.parse
from typing import List, Tuple


class ValidationError(ValueError):
    """Custom exception for validation errors"""
    pass


class ConfigValidator:
    """Advanced validation for generator configuration"""
    
    # Valid project name pattern (alphanumeric, hyphens, underscores)
    PROJECT_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    # Reserved project names that shouldn't be used
    RESERVED_NAMES = {
        'test', 'tests', 'src', 'lib', 'bin', 'config', 'utils', 'pages',
        'requirements', 'readme', 'license', 'main', 'app', 'core'
    }
    
    @classmethod
    def validate_project_name(cls, project_name: str) -> Tuple[bool, str]:
        """
        Validate project name with detailed feedback.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not project_name or not project_name.strip():
            return False, "Project name is required"
        
        project_name = project_name.strip()
        
        if len(project_name) < 3:
            return False, "Project name must be at least 3 characters long"
        
        if len(project_name) > 50:
            return False, "Project name must be 50 characters or less"
        
        if not cls.PROJECT_NAME_PATTERN.match(project_name):
            return False, "Project name can only contain letters, numbers, hyphens, and underscores"
        
        if project_name.lower() in cls.RESERVED_NAMES:
            return False, f"'{project_name}' is a reserved name, please choose a different name"
        
        if project_name.startswith(('-', '_')) or project_name.endswith(('-', '_')):
            return False, "Project name cannot start or end with hyphens or underscores"
        
        return True, ""
    
    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """
        Validate URL with detailed feedback.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url or not url.strip():
            return False, "URL is required"
        
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
        
        try:
            parsed = urllib.parse.urlparse(url)
            
            if not parsed.netloc:
                return False, "URL must include a domain name"
            
            if not parsed.scheme in ('http', 'https'):
                return False, "URL must use http or https protocol"
            
            # Check for common issues
            if parsed.netloc.startswith('.') or parsed.netloc.endswith('.'):
                return False, "Invalid domain name format"
            
            if '..' in parsed.netloc:
                return False, "Invalid domain name format"
            
            return True, ""
            
        except Exception:
            return False, "Invalid URL format"
    
    @classmethod
    def validate_site_name(cls, site_name: str) -> Tuple[bool, str]:
        """
        Validate site name.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not site_name or not site_name.strip():
            return False, "Site name is required"
        
        site_name = site_name.strip()
        
        if len(site_name) < 2:
            return False, "Site name must be at least 2 characters long"
        
        if len(site_name) > 100:
            return False, "Site name must be 100 characters or less"
        
        return True, ""
    
    @classmethod
    def sanitize_project_name(cls, project_name: str) -> str:
        """
        Sanitize project name by converting to valid format.
        
        Args:
            project_name: Raw project name input
            
        Returns:
            Sanitized project name
        """
        if not project_name:
            return ""
        
        # Convert to lowercase and replace invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', project_name.strip())
        
        # Remove leading/trailing underscores and hyphens
        sanitized = sanitized.strip('_-')
        
        # Collapse multiple consecutive underscores/hyphens
        sanitized = re.sub(r'[-_]+', '_', sanitized)
        
        # Ensure minimum length
        if len(sanitized) < 3:
            sanitized = f"project_{sanitized}" if sanitized else "my_project"
        
        # Ensure not reserved
        if sanitized.lower() in cls.RESERVED_NAMES:
            sanitized = f"{sanitized}_tests"
        
        return sanitized[:50]  # Truncate to max length
    
    @classmethod
    def get_validation_summary(cls, project_name: str, site_name: str, base_url: str) -> List[str]:
        """
        Get a list of all validation issues.
        
        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        
        valid_project, project_error = cls.validate_project_name(project_name)
        if not valid_project:
            errors.append(f"Project name: {project_error}")
        
        valid_site, site_error = cls.validate_site_name(site_name)
        if not valid_site:
            errors.append(f"Site name: {site_error}")
        
        valid_url, url_error = cls.validate_url(base_url)
        if not valid_url:
            errors.append(f"Base URL: {url_error}")
        
        return errors