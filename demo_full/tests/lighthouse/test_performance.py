"""
Lighthouse performance tests for Demo Full Featured Site
Tests Core Web Vitals and performance metrics
"""

import pytest
import json
import subprocess
from playwright.sync_api import Page
from pages.home_page import HomePage


class TestLighthousePerformance:
    """Lighthouse performance and Core Web Vitals tests"""
    
    @pytest.mark.lighthouse
    def test_lighthouse_performance_score(self, page: Page, base_url: str):
        """Test Lighthouse performance score meets minimum threshold"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Run Lighthouse audit (requires lighthouse CLI to be installed)
        try:
            result = subprocess.run([
                "lighthouse", 
                base_url,
                "--only-categories=performance",
                "--output=json",
                "--quiet",
                "--chrome-flags=--headless"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                pytest.skip("Lighthouse CLI not available or failed to run")
                
            lighthouse_data = json.loads(result.stdout)
            performance_score = lighthouse_data["lhr"]["categories"]["performance"]["score"]
            
            # Performance score should be at least 0.7 (70%)
            assert performance_score >= 0.7, f"Performance score {performance_score} is below threshold of 0.7"
            
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pytest.skip("Lighthouse CLI not available or timed out")
    
    @pytest.mark.lighthouse
    def test_core_web_vitals(self, page: Page, base_url: str):
        """Test Core Web Vitals metrics"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Measure Largest Contentful Paint (LCP)
        lcp_script = """
        () => {
            return new Promise((resolve) => {
                new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    resolve(lastEntry.startTime);
                }).observe({entryTypes: ['largest-contentful-paint']});
                
                // Fallback timeout
                setTimeout(() => resolve(null), 5000);
            });
        }
        """
        
        lcp_time = page.evaluate(lcp_script)
        if lcp_time:
            # LCP should be under 2.5 seconds for good performance
            assert lcp_time < 2500, f"LCP time {lcp_time}ms exceeds 2.5s threshold"
        
        # Measure First Input Delay (FID) simulation
        # Note: Real FID requires user interaction, so we test click responsiveness
        start_time = page.evaluate("Date.now()")
        
        # Find any clickable element and measure response time
        clickable = page.locator("button, a, [onclick]").first
        if clickable.count() > 0:
            clickable.click()
            end_time = page.evaluate("Date.now()")
            response_time = end_time - start_time
            
            # Response should be under 100ms for good responsiveness
            assert response_time < 100, f"Click response time {response_time}ms exceeds 100ms threshold"
    
    @pytest.mark.lighthouse  
    def test_page_load_metrics(self, page: Page, base_url: str):
        """Test various page load performance metrics"""
        # Navigate and measure load time
        start_time = page.evaluate("Date.now()")
        
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Wait for network idle to ensure page is fully loaded
        page.wait_for_load_state("networkidle")
        
        end_time = page.evaluate("Date.now()")
        total_load_time = end_time - start_time
        
        # Total load time should be reasonable (under 5 seconds)
        assert total_load_time < 5000, f"Page load time {total_load_time}ms exceeds 5s threshold"
        
        # Check Performance API metrics
        performance_metrics = page.evaluate("""
            () => {
                const timing = performance.timing;
                const navigation = performance.getEntriesByType('navigation')[0];
                
                return {
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    loadComplete: timing.loadEventEnd - timing.navigationStart,
                    firstPaint: navigation ? navigation.loadEventEnd : null,
                    domInteractive: timing.domInteractive - timing.navigationStart
                };
            }
        """)
        
        # DOM Content Loaded should be under 2 seconds
        if performance_metrics["domContentLoaded"]:
            assert performance_metrics["domContentLoaded"] < 2000, \
                f"DOM Content Loaded time {performance_metrics['domContentLoaded']}ms exceeds 2s"
        
        # DOM Interactive should be under 1.5 seconds  
        if performance_metrics["domInteractive"]:
            assert performance_metrics["domInteractive"] < 1500, \
                f"DOM Interactive time {performance_metrics['domInteractive']}ms exceeds 1.5s"
    
    @pytest.mark.lighthouse
    def test_resource_optimization(self, page: Page, base_url: str):
        """Test resource optimization (image sizes, compression, etc.)"""
        home_page = HomePage(page, base_url)
        home_page.navigate_to_home()
        
        # Get all network requests
        large_resources = []
        
        def handle_response(response):
            # Check for large uncompressed resources
            content_length = response.headers.get("content-length")
            content_encoding = response.headers.get("content-encoding")
            
            if content_length:
                size = int(content_length)
                # Flag resources over 1MB without compression
                if size > 1024 * 1024 and not content_encoding:
                    large_resources.append({
                        "url": response.url,
                        "size": size,
                        "type": response.headers.get("content-type", "unknown")
                    })
        
        page.on("response", handle_response)
        page.reload()
        page.wait_for_load_state("networkidle")
        
        assert not large_resources, f"Large uncompressed resources found: {large_resources}"
