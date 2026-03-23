package com.yojnasetu.gateway.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/** A single message within a chat session. */
@Entity
@Table(name = "chat_messages", indexes = {
        @Index(name = "idx_chat_messages_session", columnList = "session_id"),
        @Index(name = "idx_chat_messages_ts", columnList = "timestamp")
})
@Data
@NoArgsConstructor
public class ChatMessage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private ChatSession session;

    /**
     * Message role: USER or ASSISTANT
     */
    @Column(nullable = false, length = 15)
    private String role;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    /**
     * JSON array of scheme keys mentioned, e.g. ["pmkisan","nrega"]
     * Stored as text for portability; can be queried with LIKE or cast to JSONB in
     * Postgres.
     */
    @Column(columnDefinition = "TEXT")
    private String schemesmentioned;

    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime timestamp;
}
