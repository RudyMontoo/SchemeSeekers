package com.yojnasetu.gateway.controller;

import com.yojnasetu.gateway.model.StatusCheckLog;
import com.yojnasetu.gateway.repository.StatusCheckLogRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * Internal endpoints used exclusively by the AI Hub (FastAPI).
 * Handles status check log persistence and cache lookup for Supabase.
 */
@RestController
@RequestMapping("/api/internal/status")
public class InternalStatusController {

    @Autowired
    private StatusCheckLogRepository statusLogRepo;

    public record LogStatusRequest(
            String schemeKey,
            String maskedIdentifier,
            String resultStage,
            Long responseTimeMs,
            Boolean cached,
            String stateCode) {
    }

    // ── LOG a status check ────────────────────────────────────────────────────
    @PostMapping("/log")
    public ResponseEntity<?> logStatus(@RequestBody LogStatusRequest req) {
        StatusCheckLog log = new StatusCheckLog();
        log.setSchemeKey(req.schemeKey());
        log.setMaskedIdentifier(req.maskedIdentifier());
        log.setResultStage(req.resultStage());
        log.setResponseTimeMs(req.responseTimeMs());
        log.setCached(req.cached() != null ? req.cached() : false);
        log.setStateCode(req.stateCode());
        log.setCheckedAt(LocalDateTime.now());
        statusLogRepo.save(log);
        return ResponseEntity.ok(Map.of("status", "logged"));
    }

    // ── CHECK cache (last 30 min for same scheme+identifier) ─────────────────
    @GetMapping("/cache")
    public ResponseEntity<?> checkCache(
            @RequestParam String schemeKey,
            @RequestParam String maskedIdentifier) {
        LocalDateTime thirtyMinsAgo = LocalDateTime.now().minusMinutes(30);
        List<StatusCheckLog> results = statusLogRepo
                .findRecentSuccessfulLogs(schemeKey, maskedIdentifier, thirtyMinsAgo);

        if (results.isEmpty()) {
            return ResponseEntity.ok(Map.of("hit", false));
        }
        StatusCheckLog log = results.get(0);
        return ResponseEntity.ok(Map.<String, Object>of(
                "hit", true,
                "resultStage", log.getResultStage(),
                "checkedAt", log.getCheckedAt().toString()));
    }

    // ── ANALYTICS: popular schemes ────────────────────────────────────────────
    @GetMapping("/analytics/popular")
    public ResponseEntity<?> popularSchemes(@RequestParam(defaultValue = "5") int limit) {
        List<Object[]> results = statusLogRepo.findPopularSchemes(limit);
        List<Map<String, Object>> data = results.stream()
                .map(r -> Map.<String, Object>of("scheme_key", r[0], "count", r[1]))
                .toList();
        return ResponseEntity.ok(data);
    }
}
