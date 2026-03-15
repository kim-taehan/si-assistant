
## DDL
```sql
CREATE TABLE chat_session (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    title VARCHAR(200),
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, session_id)
);
CREATE INDEX idx_user_id ON chat_session (user_id);

CREATE TABLE chat_message (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    turn INTEGER NOT NULL,                -- 같은 턴 번호
    role VARCHAR(20) NOT NULL,      -- 'user' 또는 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 사용자+세션별 빠른 조회용 인덱스
CREATE INDEX idx_chat_message_session ON chat_message (session_id);


CREATE TABLE document (
    id BIGSERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,              -- 파일 사이즈(byte)
    uploaded_by VARCHAR(50) NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expire_at DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
);
```