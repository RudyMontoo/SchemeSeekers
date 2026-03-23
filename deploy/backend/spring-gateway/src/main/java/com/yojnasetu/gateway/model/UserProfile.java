package com.yojnasetu.gateway.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * Extended profile for a registered user.
 * These socioeconomic fields determine scheme eligibility
 * and are used by the /api/profile/matching-schemes endpoint.
 */
@Entity
@Table(name = "user_profiles")
@Data
@NoArgsConstructor
public class UserProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private User user;

    /** District within the state */
    @Column(length = 100)
    private String district;

    /** Annual family income in INR */
    private Long annualIncomeInr;

    /**
     * Occupation type: FARMER, DAILY_WAGE, SELF_EMPLOYED, GOVT_EMPLOYEE,
     * UNEMPLOYED, OTHER
     */
    @Column(length = 30)
    private String occupation;

    /** Number of people in the family */
    private Integer familySize;

    /** Does the user have a BPL (Below Poverty Line) ration card? */
    private Boolean hasBplCard;

    /** Does the user have a regular ration card? */
    private Boolean hasRationCard;

    /** Aadhaar enrollment confirmed (we never store the number itself here) */
    private Boolean hasAadhaar;

    /** Has a bank account linked to Aadhaar */
    private Boolean hasBankAccount;

    /** Does the user have any disability? */
    private Boolean hasDisability;

    /** Disability percentage (if applicable, 0-100) */
    private Integer disabilityPercentage;

    /** Is the user a farmer? */
    private Boolean isFarmer;

    /** Land owned in acres (for farmer-specific schemes) */
    private Double landOwnedAcres;

    /** Gender: MALE, FEMALE, OTHER */
    @Column(length = 10)
    private String gender;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
