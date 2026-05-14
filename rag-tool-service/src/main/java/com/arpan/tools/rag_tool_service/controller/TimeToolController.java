package com.arpan.tools.rag_tool_service.controller;

import org.springframework.web.bind.annotation.*;

import java.time.*;
import java.time.format.*;

@RestController
public class TimeToolController {

    @GetMapping("/tools/time")
    public String getCurrentTime(
            @RequestParam(defaultValue = "Asia/Kolkata") String zone
    ) {
        ZonedDateTime now = ZonedDateTime.now(ZoneId.of(zone));

        return "Current time in " + zone + " is " +
                now.format(DateTimeFormatter.ofPattern("dd MMM yyyy, hh:mm a"));
    }
}