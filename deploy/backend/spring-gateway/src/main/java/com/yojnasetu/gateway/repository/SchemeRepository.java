package com.yojnasetu.gateway.repository;

import com.yojnasetu.gateway.model.Scheme;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.List;

@Repository
public interface SchemeRepository extends JpaRepository<Scheme, Long> {
    Optional<Scheme> findBySchemeKey(String schemeKey);
    List<Scheme> findByIsActiveTrue();
}
