package com.yojnasetu.gateway.controller;

import com.yojnasetu.gateway.model.ChatMessage;
import com.yojnasetu.gateway.model.ChatSession;
import com.yojnasetu.gateway.repository.ChatMessageRepository;
import com.yojnasetu.gateway.repository.ChatSessionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Internal endpoints used exclusively by the AI Hub (FastAPI).
 * These are NOT meant for the frontend — they bypass JWT authentication
 * since they are called service-to-service on the private network.
 */
@RestController
@RequestMapping("/api/internal/chat")
public class InternalChatController {

    @Autowired
    private ChatSessionRepository sessionRepo;

    @Autowired
    private ChatMessageRepository messageRepo;

    public record CreateSessionRequest(
            String sessionId,
            String language,
            String state,
            String sessionType) {
    }

    public record SaveMessageRequest(
            String sessionId,
            String role, // "user" or "assistant"
            String content,
            String schemesMentioned) {
    } // JSON array string, nullable

    // ── GET or CREATE session ─────────────────────────────────────────────────
    @PostMapping("/session")
    public ResponseEntity<?> getOrCreateSession(@RequestBody CreateSessionRequest req) {
        ChatSession session = sessionRepo.findBySessionId(req.sessionId()).orElseGet(() -> {
            ChatSession s = new ChatSession();
            s.setSessionId(req.sessionId());
            s.setLanguage(req.language() != null ? req.language() : "hinglish");
            s.setState(req.state());
            s.setSessionType(req.sessionType() != null ? req.sessionType() : "CHAT");
            return sessionRepo.save(s);
        });
        return ResponseEntity.ok(Map.of(
                "id", session.getId(),
                "sessionId", session.getSessionId(),
                "language", session.getLanguage() != null ? session.getLanguage() : "hinglish",
                "state", session.getState() != null ? session.getState() : ""));
    }

    // ── SAVE message ──────────────────────────────────────────────────────────
    @PostMapping("/message")
    public ResponseEntity<?> saveMessage(@RequestBody SaveMessageRequest req) {
        Optional<ChatSession> sessionOpt = sessionRepo.findBySessionId(req.sessionId());
        if (sessionOpt.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Session not found: " + req.sessionId()));
        }
        ChatSession session = sessionOpt.get();
        ChatMessage msg = new ChatMessage();
        msg.setSession(session);
        msg.setRole(req.role());
        msg.setContent(req.content());
        msg.setSchemesmentioned(req.schemesMentioned());
        messageRepo.save(msg);
        return ResponseEntity.ok(Map.of("status", "saved"));
    }

    // ── GET history ───────────────────────────────────────────────────────────
    @GetMapping("/session/{sessionId}/history")
    public ResponseEntity<?> getHistory(@PathVariable String sessionId,
            @RequestParam(defaultValue = "12") int limit) {
        Optional<ChatSession> sessionOpt = sessionRepo.findBySessionId(sessionId);
        if (sessionOpt.isEmpty()) {
            return ResponseEntity.ok(Map.of("session_id", sessionId, "messages", List.of()));
        }
        ChatSession session = sessionOpt.get();
        List<ChatMessage> messages = messageRepo.findBySessionOrderByTimestampAsc(session);
        int start = Math.max(0, messages.size() - limit);
        List<Map<String, Object>> result = messages.subList(start, messages.size()).stream()
                .map(m -> Map.<String, Object>of(
                        "role", m.getRole(),
                        "content", m.getContent(),
                        "timestamp", m.getTimestamp() != null ? m.getTimestamp().toString() : "",
                        "schemes", m.getSchemesmentioned() != null ? m.getSchemesmentioned() : ""))
                .toList();
        return ResponseEntity.ok(Map.of("session_id", sessionId, "messages", result));
    }

    // ── CLEAR session ──────────────────────────────────────────────────────────
    @DeleteMapping("/session/{sessionId}")
    public ResponseEntity<?> clearSession(@PathVariable String sessionId) {
        sessionRepo.findBySessionId(sessionId).ifPresent(s -> {
            messageRepo.deleteBySession(s);
            sessionRepo.delete(s);
        });
        return ResponseEntity.ok(Map.of("status", "cleared", "session_id", sessionId));
    }
}
