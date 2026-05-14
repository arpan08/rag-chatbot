package com.arpan.tools.rag_tool_service.controller;


import org.springframework.beans.factory.annotation.*;
import org.springframework.web.bind.annotation.*;
import tools.jackson.databind.*;

import java.io.*;
import java.net.*;
import java.nio.charset.*;

@RestController
public class WeatherToolController {

    @Value("${weather.api-key}")
    private String apiKey;

    @Value("${weather.base-url}")
    private String baseUrl;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @GetMapping("/tools/weather")
    public String getWeather(@RequestParam String city) {
        try {
            String encodedCity = URLEncoder.encode(city, StandardCharsets.UTF_8);

            String urlString = baseUrl
                    + "?q=" + encodedCity
                    + "&appid=" + apiKey
                    + "&units=metric";

            URL url = new URL(urlString);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");

            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(connection.getInputStream())
            );

            StringBuilder response = new StringBuilder();
            String line;

            while ((line = reader.readLine()) != null) {
                response.append(line);
            }

            reader.close();

            JsonNode root = objectMapper.readTree(response.toString());

            String cityName = root.path("name").asText(city);
            double temp = root.path("main").path("temp").asDouble();
            double feelsLike = root.path("main").path("feels_like").asDouble();
            int humidity = root.path("main").path("humidity").asInt();
            double windSpeed = root.path("wind").path("speed").asDouble();
            String description = root.path("weather").get(0).path("description").asText();

            return "Weather in " + cityName + ": "
                    + temp + "°C, " + description
                    + ". Feels like " + feelsLike + "°C"
                    + ". Humidity: " + humidity + "%"
                    + ". Wind speed: " + windSpeed + " m/s.";

        } catch (Exception e) {
            return "Unable to fetch weather for city: " + city;
        }
    }
}