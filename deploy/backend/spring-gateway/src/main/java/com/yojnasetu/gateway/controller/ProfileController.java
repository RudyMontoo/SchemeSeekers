package com.yojnasetu.gateway.controller;

import com.yojnasetu.gateway.model.Scheme;
import com.yojnasetu.gateway.model.User;
import com.yojnasetu.gateway.model.UserProfile;
import com.yojnasetu.gateway.repository.SchemeRepository;
import com.yojnasetu.gateway.repository.UserProfileRepository;
import com.yojnasetu.gateway.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/profile")
public class ProfileController {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private UserProfileRepository userProfileRepository;

    @Autowired
    private SchemeRepository schemeRepository;

    private User getAuthenticatedUser() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || "anonymousUser".equals(auth.getPrincipal())) {
            return null;
        }
        return userRepository.findByUsername(auth.getName()).orElse(null);
    }

    @GetMapping
    public ResponseEntity<?> getProfile() {
        User user = getAuthenticatedUser();
        if (user == null)
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();

        UserProfile profile = userProfileRepository.findByUser(user).orElse(new UserProfile());
        return ResponseEntity.ok(Map.of("user", user, "profile", profile));
    }

    // Accepting a generic map gives us flexibility rather than a strict DTO for now
    @PutMapping
    public ResponseEntity<?> updateProfile(@RequestBody Map<String, Object> updates) {
        User user = getAuthenticatedUser();
        if (user == null)
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();

        UserProfile profile = userProfileRepository.findByUser(user).orElse(new UserProfile());
        profile.setUser(user);

        // Update User-level fields
        if (updates.containsKey("age"))
            user.setAge((Integer) updates.get("age"));
        if (updates.containsKey("category"))
            user.setCategory((String) updates.get("category"));
        if (updates.containsKey("phoneNumber"))
            user.setPhoneNumber((String) updates.get("phoneNumber"));
        if (updates.containsKey("state"))
            user.setState((String) updates.get("state"));
        if (updates.containsKey("language"))
            user.setLanguage((String) updates.get("language"));

        // Update UserProfile-level fields
        if (updates.containsKey("district"))
            profile.setDistrict((String) updates.get("district"));
        if (updates.containsKey("annualIncomeInr")) {
            Object inc = updates.get("annualIncomeInr");
            profile.setAnnualIncomeInr(inc instanceof Number ? ((Number) inc).longValue() : null);
        }
        if (updates.containsKey("occupation"))
            profile.setOccupation((String) updates.get("occupation"));
        if (updates.containsKey("familySize"))
            profile.setFamilySize((Integer) updates.get("familySize"));
        if (updates.containsKey("hasBplCard"))
            profile.setHasBplCard((Boolean) updates.get("hasBplCard"));
        if (updates.containsKey("hasRationCard"))
            profile.setHasRationCard((Boolean) updates.get("hasRationCard"));
        if (updates.containsKey("hasAadhaar"))
            profile.setHasAadhaar((Boolean) updates.get("hasAadhaar"));
        if (updates.containsKey("hasBankAccount"))
            profile.setHasBankAccount((Boolean) updates.get("hasBankAccount"));
        if (updates.containsKey("hasDisability"))
            profile.setHasDisability((Boolean) updates.get("hasDisability"));
        if (updates.containsKey("isFarmer"))
            profile.setIsFarmer((Boolean) updates.get("isFarmer"));
        if (updates.containsKey("gender"))
            profile.setGender((String) updates.get("gender"));

        userRepository.save(user);
        userProfileRepository.save(profile);

        return ResponseEntity.ok(Map.of("message", "Profile updated successfully"));
    }

    @GetMapping("/matching-schemes")
    public ResponseEntity<?> getMatchingSchemes() {
        User user = getAuthenticatedUser();
        if (user == null)
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();

        UserProfile profile = userProfileRepository.findByUser(user).orElse(null);
        List<Scheme> allSchemes = schemeRepository.findByIsActiveTrue();

        List<Scheme> matched = allSchemes.stream().filter(s -> {
            boolean isMatch = true;
            if (s.getTargetGender() != null && profile != null && profile.getGender() != null) {
                if (!s.getTargetGender().equalsIgnoreCase("ALL")
                        && !s.getTargetGender().equalsIgnoreCase(profile.getGender())) {
                    isMatch = false;
                }
            }
            if (s.getMaxAnnualIncomeInr() != null && profile != null && profile.getAnnualIncomeInr() != null) {
                if (profile.getAnnualIncomeInr() > s.getMaxAnnualIncomeInr()) {
                    isMatch = false;
                }
            }
            if (s.getMinAge() != null && user.getAge() != null) {
                if (user.getAge() < s.getMinAge())
                    isMatch = false;
            }
            if (s.getMaxAge() != null && user.getAge() != null) {
                if (user.getAge() > s.getMaxAge())
                    isMatch = false;
            }
            return isMatch;
        }).collect(Collectors.toList());

        return ResponseEntity.ok(matched);
    }
}
