"""
Weather Tool extension for Open WebUI.

This extension demonstrates how to create a tool extension that adds
both UI components and API endpoints.
"""

import logging
from typing import Dict, List, Any

from open_webui_extensions import (
    ToolExtension,
    hook,
    ui_component,
    api_route,
    tool,
    setting,
)

logger = logging.getLogger("weather-tool-extension")

@setting(name="api_key", default="", description="Your weather API key (demo mode if empty)")
@setting(name="default_location", default="London", description="Default location for weather lookups")
@setting(name="temperature_unit", default="metric", options=[
    {"label": "Celsius (Metric)", "value": "metric"},
    {"label": "Fahrenheit (Imperial)", "value": "imperial"}
], description="Temperature unit")
class WeatherToolExtension(ToolExtension):
    """A weather tool extension."""
    
    @property
    def name(self) -> str:
        return "weather-tool"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    @property
    def description(self) -> str:
        return "A weather tool extension for Open WebUI."
    
    @property
    def author(self) -> str:
        return "Open WebUI Team"
    
    @property
    def components(self) -> Dict[str, Any]:
        return {
            "weather_widget": self.render_weather_widget,
        }
    
    @property
    def mount_points(self) -> Dict[str, List[str]]:
        return {
            "sidebar": ["weather_widget"],
        }
    
    @property
    def tools(self) -> Dict[str, Any]:
        return {
            "get_weather": self.get_weather_tool,
        }
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the extension."""
        logger.info("Initializing Weather Tool extension")
        return True
    
    def activate(self) -> bool:
        """Activate the extension."""
        logger.info("Activating Weather Tool extension")
        return True
    
    def deactivate(self) -> bool:
        """Deactivate the extension."""
        logger.info("Deactivating Weather Tool extension")
        return True
    
    @ui_component("weather_widget", mount_points=["sidebar"])
    def render_weather_widget(self) -> Dict[str, Any]:
        """Render the weather widget component."""
        return {
            "html": f"""
            <div class="weather-widget" style="padding: 1rem; background-color: #f8f9fa; border-radius: 0.25rem; margin: 0.5rem 0;">
                <h3>Weather Tool</h3>
                <div id="weather-results">
                    <p>Enter a location to check the weather.</p>
                </div>
                <div class="weather-form">
                    <input type="text" id="weather-location" placeholder="Location" value="{self.default_location}">
                    <button id="weather-search-btn">Search</button>
                </div>
                
                <script>
                    document.getElementById('weather-search-btn').addEventListener('click', async () => {
                        const location = document.getElementById('weather-location').value;
                        const resultsDiv = document.getElementById('weather-results');
                        
                        resultsDiv.innerHTML = '<p>Loading weather data...</p>';
                        
                        try {
                            const response = await fetch(`/api/extensions/weather-tool/weather/${encodeURIComponent(location)}`);
                            const data = await response.json();
                            
                            if (data.success) {
                                resultsDiv.innerHTML = `
                                    <div style="text-align: center; padding: 0.5rem; margin-top: 0.5rem;">
                                        <h4>${data.location}</h4>
                                        <div class="weather-info">
                                            <p class="temperature">${data.weather.temperature}°${data.weather.unit === 'metric' ? 'C' : 'F'}</p>
                                            <p>${data.weather.description}</p>
                                        </div>
                                    </div>
                                `;
                            } else {
                                resultsDiv.innerHTML = `<p class="error">${data.message || 'Failed to get weather data'}</p>`;
                            }
                        } catch (error) {
                            resultsDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
                        }
                    });
                </script>
            </div>
            """
        }
    
    @api_route("/weather/{location}", methods=["GET"])
    async def get_weather_api(self, location: str) -> Dict[str, Any]:
        """API endpoint to get weather data."""
        weather_data = self._get_weather_data(location)
        
        if weather_data:
            return {
                "success": True,
                "location": location,
                "weather": weather_data,
            }
        else:
            return {
                "success": False,
                "message": f"Failed to get weather data for {location}",
            }
    
    @tool("get_weather")
    def get_weather_tool(self, location: str = None) -> Dict[str, Any]:
        """
        Get weather information for a specific location.
        
        Args:
            location: The location to get weather for (city name).
        
        Returns:
            A dictionary containing weather information.
        """
        location = location or self.default_location
        return self._get_weather_data(location)
    
    def _get_weather_data(self, location: str) -> Dict[str, Any]:
        """Get weather data for a location.
        
        This is a mock implementation. In a real extension, you would
        call an actual weather API here.
        
        Args:
            location: The location to get weather for.
            
        Returns:
            A dictionary containing weather information.
        """
        # In a real extension, you would use the API key to call a weather API
        # Since this is a demo, we'll return mock data
        import random
        
        # Convert location to lowercase for case-insensitive comparison
        location_lower = location.lower()
        
        # Mock data for specific cities
        mock_data = {
            "london": {
                "temperature": 15,
                "description": "Cloudy with a chance of rain",
            },
            "new york": {
                "temperature": 22,
                "description": "Sunny with scattered clouds",
            },
            "tokyo": {
                "temperature": 26,
                "description": "Clear skies",
            },
            "sydney": {
                "temperature": 20,
                "description": "Partly cloudy",
            },
            "paris": {
                "temperature": 18,
                "description": "Light rain",
            },
        }
        
        # If we have mock data for this city, use it
        if location_lower in mock_data:
            data = mock_data[location_lower]
        else:
            # Generate random weather for unknown locations
            temp_base = random.randint(5, 35)
            descriptions = [
                "Sunny", "Partly cloudy", "Cloudy", 
                "Light rain", "Heavy rain", "Thunderstorms",
                "Snowy", "Foggy", "Clear skies"
            ]
            data = {
                "temperature": temp_base,
                "description": random.choice(descriptions),
            }
        
        # Convert temperature if needed
        if self.temperature_unit == "imperial":
            # Convert from Celsius to Fahrenheit
            data["temperature"] = round((data["temperature"] * 9/5) + 32)
        
        # Add the unit to the data
        data["unit"] = self.temperature_unit
        
        return data

# Create an instance of the extension
extension = WeatherToolExtension()
