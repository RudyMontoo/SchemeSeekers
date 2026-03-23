package com.yojnasetu.gateway.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * Tracks every interaction a user has with a scheme:
 * viewing it, bookmarking it, or submitting an application.
 */
@Entity
@Table(name = "user_scheme_interactions", indexes = {
        @Index(name = "idx_usi_user", columnList = "user_id"),
        @Index(name = "idx_usi_scheme", columnList = "scheme_id"),
        @Index(name = "idx_usi_type", columnList = "interaction_type")
})
@Data
@NoArgsConstructor
public class UserSchemeInteraction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "scheme_id", nullable = false)
    private Scheme scheme;

    /**
     * Type of interaction:
     * VIEWED — user read about this scheme in chat
     * BOOKMARKED — user explicitly saved it
     * APPLIED — user started the application wizard
     */
    @Column(name = "interaction_type", nullable = false, length = 20)
    private String interactionType;

    /** Application reference ID, if the user has applied */
    @Column(length = 100)
    private String applicationId;

    /** Current application status, if known */
    @Column(length = 100)
    private String applicationStatus;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime timestamp;
}
