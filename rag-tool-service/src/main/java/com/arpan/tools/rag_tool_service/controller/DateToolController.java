package com.arpan.tools.rag_tool_service.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

@RestController
public class DateToolController {

    @GetMapping("/tools/date")
    public String getCurrentDate() {
        System.out.println("date is calling");
        return "Today's date is " +
                LocalDate.now().format(DateTimeFormatter.ofPattern("dd MMM yyyy"));
    }
}