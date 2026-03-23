package com.yojnasetu.gateway.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * Logs every call to the status-checker endpoint.
 * The identifier is always stored MASKED (e.g. XXXX-XXXX-1234) — never raw.
 */
@Entity
@Table(name = "status_check_logs", indexes = {
        @Index(name = "idx_scl_user", columnList = "user_id"),
        @Index(name = "idx_scl_scheme", columnList = "scheme_key"),
        @Index(name = "idx_scl_ts", columnList = "checked_at")
})
@Data
@NoArgsConstructor
public class StatusCheckLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Can be null for guest users */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;

    /** e.g. "pmkisan", "nrega" */
    @Column(name = "scheme_key", nullable = false, length = 50)
    private String schemeKey;

    /** PII-masked identifier, e.g. "XXXXXXXX-1234" */
    @Column(name = "masked_identifier", length = 50)
    private String maskedIdentifier;

    /** The stage returned by the status check */
    @Column(name = "result_stage", length = 200)
    private String resultStage;

    /** How long the government portal took to reply (ms) */
    private Long responseTimeMs;

    /** Whether the result was served from cache */
    private Boolean cached = false;

    /** Optional state code for stateful schemes (NREGA) */
    @Column(length = 10)
    private String stateCode;

    @Column(name = "checked_at", updatable = false)
    @CreationTimestamp
    private LocalDateTime checkedAt;
}
