package com.yojnasetu.gateway.controller;

import com.yojnasetu.gateway.model.User;
import com.yojnasetu.gateway.model.UserProfile;
import com.yojnasetu.gateway.repository.UserProfileRepository;
import com.yojnasetu.gateway.repository.UserRepository;
import com.yojnasetu.gateway.security.JwtUtils;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

        @Autowired
        private AuthenticationManager authManager;
        @Autowired
        private UserRepository userRepo;
        @Autowired
        private UserProfileRepository profileRepo;
        @Autowired
        private PasswordEncoder passwordEncoder;
        @Autowired
        private JwtUtils jwtUtils;

        // ── DTOs ───────────────────────────────────────────────────────────────────
        public record RegisterRequest(
                        @NotBlank @Size(min = 3, max = 30) String username,
                        @NotBlank @Email String email,
                        @NotBlank @Size(min = 6) String password,
                        String state,
                        String language,
                        String phoneNumber,
                        Integer age,
                        String category,
                        String district,
                        Long annualIncomeInr,
                        String occupation,
                        Integer familySize,
                        Boolean hasBplCard,
                        Boolean hasRationCard,
                        Boolean hasAadhaar,
                        Boolean hasBankAccount,
                        Boolean hasDisability,
                        Boolean isFarmer,
                        String gender) {
        }

        public record LoginRequest(
                        @NotBlank String username,
                        @NotBlank String password) {
        }

        public record ChangePasswordRequest(
                        @NotBlank String oldPassword,
                        @NotBlank @Size(min = 6) String newPassword) {
        }

        // ── Register ───────────────────────────────────────────────────────────────
        @PostMapping("/register")
        public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest req) {
                if (userRepo.existsByUsername(req.username())) {
                        return ResponseEntity.status(HttpStatus.CONFLICT)
                                        .body(Map.of("error", "Username already taken"));
                }
                if (userRepo.existsByEmail(req.email())) {
                        return ResponseEntity.status(HttpStatus.CONFLICT)
                                        .body(Map.of("error", "Email already registered"));
                }

                User user = new User(req.username(), req.email(), passwordEncoder.encode(req.password()));
                user.setState(req.state());
                user.setLanguage(req.language() != null ? req.language() : "hi-IN");
                user.setPhoneNumber(req.phoneNumber());
                user.setAge(req.age());
                user.setCategory(req.category());
                userRepo.save(user);

                UserProfile profile = new UserProfile();
                profile.setUser(user);
                profile.setDistrict(req.district());
                profile.setAnnualIncomeInr(req.annualIncomeInr());
                profile.setOccupation(req.occupation());
                profile.setFamilySize(req.familySize());
                profile.setHasBplCard(req.hasBplCard());
                profile.setHasRationCard(req.hasRationCard());
                profile.setHasAadhaar(req.hasAadhaar());
                profile.setHasBankAccount(req.hasBankAccount());
                profile.setHasDisability(req.hasDisability());
                profile.setIsFarmer(req.isFarmer());
                profile.setGender(req.gender());
                profileRepo.save(profile);

                String token = jwtUtils.generateToken(user.getUsername());
                return ResponseEntity.ok(Map.of(
                                "token", token,
                                "username", user.getUsername(),
                                "message", "Registration successful! Yojna Setu mein aapka swagat hai! 🙏"));
        }

        // ── Login ──────────────────────────────────────────────────────────────────
        @PostMapping("/login")
        public ResponseEntity<?> login(@Valid @RequestBody LoginRequest req) {
                try {
                        Authentication auth = authManager.authenticate(
                                        new UsernamePasswordAuthenticationToken(req.username(), req.password()));
                        String token = jwtUtils.generateToken(auth.getName());
                        User user = userRepo.findByUsername(auth.getName()).orElseThrow();
                        return ResponseEntity.ok(Map.of(
                                        "token", token,
                                        "username", user.getUsername(),
                                        "state", user.getState() != null ? user.getState() : "",
                                        "language", user.getLanguage() != null ? user.getLanguage() : "hi-IN"));
                } catch (Exception e) {
                        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                                        .body(Map.of("error", "Invalid username or password"));
                }
        }

        // ── Change Password ────────────────────────────────────────────────────────
        @PostMapping("/change-password")
        public ResponseEntity<?> changePassword(
                        @Valid @RequestBody ChangePasswordRequest req,
                        org.springframework.security.core.Authentication authentication) {
                if (authentication == null || !authentication.isAuthenticated()) {
                        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                                        .body(Map.of("error", "Not authenticated"));
                }
                String username = authentication.getName();
                User user = userRepo.findByUsername(username).orElse(null);
                if (user == null) {
                        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                                        .body(Map.of("error", "User not found"));
                }
                if (!passwordEncoder.matches(req.oldPassword(), user.getPasswordHash())) {
                        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                                        .body(Map.of("error", "Current password is incorrect"));
                }
                user.setPasswordHash(passwordEncoder.encode(req.newPassword()));
                userRepo.save(user);
                return ResponseEntity.ok(Map.of("message", "Password updated successfully"));
        }
}
