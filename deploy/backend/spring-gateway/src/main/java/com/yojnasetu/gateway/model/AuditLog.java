package com.yojnasetu.gateway.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * Immutable audit trail — every important user action is recorded here.
 * Never update or delete rows in this table.
 */
@Entity
@Table(name = "audit_log", indexes = {
        @Index(name = "idx_audit_user", columnList = "user_id"),
        @Index(name = "idx_audit_action", columnList = "action"),
        @Index(name = "idx_audit_ts", columnList = "timestamp")
})
@Data
@NoArgsConstructor
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** User who performed the action (null for anonymous) */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;

    /**
     * Action performed, e.g.:
     * USER_REGISTERED, USER_LOGIN, USER_LOGIN_FAILED,
     * PROFILE_UPDATED, SCHEME_VIEWED, SCHEME_BOOKMARKED,
     * STATUS_CHECKED, CHAT_STARTED, VOICE_SESSION_STARTED
     */
    @Column(nullable = false, length = 50)
    private String action;

    /** Type of resource involved: USER, SCHEME, CHAT_SESSION, STATUS_CHECK */
    @Column(length = 30)
    private String resourceType;

    /** ID of the resource (e.g. scheme key, session ID) */
    @Column(length = 100)
    private String resourceId;

    /** Client IP address (anonymized last octet: "192.168.1.xxx") */
    @Column(length = 20)
    private String ipAddress;

    /** Additional context in JSON format */
    @Column(columnDefinition = "TEXT")
    private String details;

    @Column(nullable = false, updatable = false)
    @CreationTimestamp
    private LocalDateTime timestamp;
}
