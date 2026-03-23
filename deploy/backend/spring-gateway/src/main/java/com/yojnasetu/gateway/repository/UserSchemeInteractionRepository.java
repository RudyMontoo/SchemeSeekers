package com.yojnasetu.gateway.repository;

import com.yojnasetu.gateway.model.UserSchemeInteraction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserSchemeInteractionRepository extends JpaRepository<UserSchemeInteraction, Long> {
}
