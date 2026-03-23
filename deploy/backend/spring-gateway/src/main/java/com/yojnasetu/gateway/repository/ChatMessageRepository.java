package com.yojnasetu.gateway.repository;

import com.yojnasetu.gateway.model.ChatMessage;
import com.yojnasetu.gateway.model.ChatSession;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {
    List<ChatMessage> findBySessionOrderByTimestampAsc(ChatSession session);

    void deleteBySession(ChatSession session);
}
