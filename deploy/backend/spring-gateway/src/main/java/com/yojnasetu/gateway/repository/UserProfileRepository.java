package com.yojnasetu.gateway.repository;

import com.yojnasetu.gateway.model.UserProfile;
import com.yojnasetu.gateway.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface UserProfileRepository extends JpaRepository<UserProfile, Long> {
    Optional<UserProfile> findByUser(User user);
}
