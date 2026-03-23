package com.yojnasetu.gateway.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/** A single conversation session between a user (or guest) and the AI. */
@Entity
@Table(name = "chat_sessions", indexes = {
        @Index(name = "idx_chat_sessions_sid", columnList = "session_id"),
        @Index(name = "idx_chat_sessions_user", columnList = "user_id")
})
@Data
@NoArgsConstructor
public class ChatSession {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** The UUID session identifier passed by the client */
    @Column(name = "session_id", unique = true, nullable = false, length = 100)
    private String sessionId;

    /** Null for unauthenticated / guest users */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;

    /** Language used in this session, e.g. "hi-IN" */
    @Column(length = 10)
    private String language;

    /** Indian state context, e.g. "Bihar" */
    @Column(length = 50)
    private String state;

    /** Type of session: CHAT, AGENT, VOICE */
    @Column(length = 20)
    private String sessionType;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime startedAt;

    @UpdateTimestamp
    private LocalDateTime lastActivityAt;
}
