package com.yojnasetu.gateway.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * Government scheme entity — replaces the flat schemes_lite.json file.
 * Seeded by Flyway V2 migration script.
 */
@Entity
@Table(name = "schemes", indexes = {
        @Index(name = "idx_schemes_key", columnList = "scheme_key"),
        @Index(name = "idx_schemes_sector", columnList = "sector")
})
@Data
@NoArgsConstructor
public class Scheme {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Short unique identifier, e.g. "pmkisan", "nrega" */
    @Column(name = "scheme_key", unique = true, nullable = false, length = 50)
    private String schemeKey;

    @Column(nullable = false, length = 200)
    private String name;

    /** Sector: AGRICULTURE, HOUSING, EDUCATION, HEALTH, WOMEN, EMPLOYMENT, etc. */
    @Column(length = 50)
    private String sector;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(columnDefinition = "TEXT")
    private String eligibility;

    @Column(length = 500)
    private String benefit;

    @Column(length = 300)
    private String applyUrl;

    @Column(length = 20)
    private String helpline;

    /** Minimum age to be eligible (null = no restriction) */
    private Integer minAge;
    private Integer maxAge;

    /** Target gender: ALL, FEMALE, MALE */
    @Column(length = 10)
    private String targetGender;

    /** Target social category: ALL, SC, ST, OBC, GENERAL, EWS */
    @Column(length = 20)
    private String targetCategory;

    /** Maximum annual household income in INR to be eligible */
    private Long maxAnnualIncomeInr;

    /** Whether this scheme is currently active/available */
    @Column(nullable = false)
    private boolean isActive = true;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
