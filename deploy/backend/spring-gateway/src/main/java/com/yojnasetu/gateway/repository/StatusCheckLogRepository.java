package com.yojnasetu.gateway.repository;

import com.yojnasetu.gateway.model.StatusCheckLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface StatusCheckLogRepository extends JpaRepository<StatusCheckLog, Long> {

    /**
     * Cache lookup: find the most recent successful log for a scheme+identifier
     * within a given time window, excluding error results.
     */
    @Query("SELECT s FROM StatusCheckLog s WHERE s.schemeKey = :schemeKey " +
            "AND s.maskedIdentifier = :maskedId " +
            "AND s.checkedAt >= :since " +
            "AND s.resultStage NOT LIKE '%Check portal directly%' " +
            "AND s.resultStage NOT LIKE '%Unable to fetch%' " +
            "ORDER BY s.checkedAt DESC")
    List<StatusCheckLog> findRecentSuccessfulLogs(
            @Param("schemeKey") String schemeKey,
            @Param("maskedId") String maskedIdentifier,
            @Param("since") LocalDateTime since);

    /**
     * Analytics: most frequently checked schemes.
     */
    @Query(value = "SELECT s.scheme_key, COUNT(s.id) as cnt FROM status_check_logs s " +
            "GROUP BY s.scheme_key ORDER BY cnt DESC LIMIT :limit", nativeQuery = true)
    List<Object[]> findPopularSchemes(@Param("limit") int limit);
}
