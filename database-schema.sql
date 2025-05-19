-- Extension for hierarchical data structures
CREATE EXTENSION IF NOT EXISTS ltree;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations table for multi-tenancy
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
	uuid UUID DEFAULT uuid_generate_v4(),
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    password_hash TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, username)
);

-- MFT (Moral Foundation Theory) Profiles
CREATE TABLE mft_profiles (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    care_harm FLOAT DEFAULT 0.0 CHECK (care_harm BETWEEN 0.0 AND 1.0),
    fairness_cheating FLOAT DEFAULT 0.0 CHECK (fairness_cheating BETWEEN 0.0 AND 1.0),
    loyalty_betrayal FLOAT DEFAULT 0.0 CHECK (loyalty_betrayal BETWEEN 0.0 AND 1.0),
    authority_subversion FLOAT DEFAULT 0.0 CHECK (authority_subversion BETWEEN 0.0 AND 1.0),
    sanctity_degradation FLOAT DEFAULT 0.0 CHECK (sanctity_degradation BETWEEN 0.0 AND 1.0),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, name)
);

-- User-Profile Preferences (for browser extension)
CREATE TABLE user_profile_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    mft_profile_id INTEGER REFERENCES mft_profiles(id) ON DELETE CASCADE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, mft_profile_id)
);

-- Argument maps table
CREATE TABLE argument_maps (
    id SERIAL PRIMARY KEY,
	uuid UUID DEFAULT uuid_generate_v4(),
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    creator_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    source_xml TEXT,
    version INTEGER DEFAULT 1,  -- For tracking versions
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Argument map versions for change history
CREATE TABLE argument_map_versions (
    id SERIAL PRIMARY KEY,
    argument_map_id INTEGER REFERENCES argument_maps(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    creator_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    source_xml TEXT,
    change_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(argument_map_id, version)
);


-- Statements table - for premises, conclusions, rebuttals, counter-conclusions
CREATE TABLE statements (
    id SERIAL PRIMARY KEY,
	uuid UUID DEFAULT uuid_generate_v4(),
    argument_map_id INTEGER REFERENCES argument_maps(id) ON DELETE CASCADE,
    external_id VARCHAR(100),
    statement_text TEXT NOT NULL,
    statement_type VARCHAR(50) CHECK (statement_type IN ('premise', 'conclusion', 'rebuttal', 'counter_conclusion')),
    position INTEGER,
    path LTREE,  -- Hierarchical path for efficient tree retrieval
    depth INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX statements_path_idx ON statements USING GIST (path);

-- MoralBERT Scores for statements
CREATE TABLE moralbert_scores (
    id SERIAL PRIMARY KEY,
    statement_id INTEGER REFERENCES statements(id) ON DELETE CASCADE,
    care_harm_score FLOAT CHECK (care_harm_score BETWEEN -1.0 AND 1.0),
    fairness_cheating_score FLOAT CHECK (fairness_cheating_score BETWEEN -1.0 AND 1.0),
    loyalty_betrayal_score FLOAT CHECK (loyalty_betrayal_score BETWEEN -1.0 AND 1.0),
    authority_subversion_score FLOAT CHECK (authority_subversion_score BETWEEN -1.0 AND 1.0),
    sanctity_degradation_score FLOAT CHECK (sanctity_degradation_score BETWEEN -1.0 AND 1.0),
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Statement relationships - captures support/oppose and linked premises
CREATE TABLE statement_relationships (
    id SERIAL PRIMARY KEY,
	uuid UUID DEFAULT uuid_generate_v4(),
    argument_map_id INTEGER REFERENCES argument_maps(id) ON DELETE CASCADE,
    from_statement_id INTEGER REFERENCES statements(id) ON DELETE CASCADE,
    to_statement_id INTEGER REFERENCES statements(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) CHECK (relationship_type IN ('support', 'oppose')),
    convergence_group_id UUID,  -- For linked premises (NULL if independent)
    strength FLOAT CHECK (strength BETWEEN 0 AND 1),  -- Optional relationship strength
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_statement_id, to_statement_id)
);

-- Cross-map references - allowing one argument map to reference another
CREATE TABLE cross_map_references (
    id SERIAL PRIMARY KEY,
    source_map_id INTEGER REFERENCES argument_maps(id) ON DELETE CASCADE,
    target_map_id INTEGER REFERENCES argument_maps(id) ON DELETE CASCADE,
    source_statement_id INTEGER REFERENCES statements(id) ON DELETE CASCADE,
    reference_type VARCHAR(50) CHECK (reference_type IN ('support', 'oppose', 'example', 'elaboration')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_statement_id, target_map_id)
);

CREATE TABLE evidence (
    id SERIAL PRIMARY KEY,
	uuid UUID DEFAULT uuid_generate_v4(),
    argument_map_id INTEGER REFERENCES argument_maps(id) ON DELETE CASCADE,
    external_id VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    source_type VARCHAR(100),  -- e.g., "academic", "news", "statistic"
    source_name VARCHAR(255),
    url TEXT,
    description TEXT,
    credibility_rating FLOAT CHECK (credibility_rating BETWEEN 0 AND 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(argument_map_id, external_id)
);

-- Entity relationships - Flexible relationship system for evidence critiques
CREATE TABLE entity_relationships (
    id SERIAL PRIMARY KEY,
	uuid UUID DEFAULT uuid_generate_v4(),
    argument_map_id INTEGER REFERENCES argument_maps(id) ON DELETE CASCADE,
    from_type VARCHAR(50) CHECK (from_type IN ('statement', 'evidence')),
    from_id INTEGER NOT NULL,
    to_type VARCHAR(50) CHECK (to_type IN ('statement', 'evidence')),
    to_id INTEGER NOT NULL,
    relationship_type VARCHAR(50) CHECK (relationship_type IN ('support', 'critique')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_type, from_id, to_type, to_id)
);

-- Browser extension settings
CREATE TABLE browser_extension_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    default_mft_profile_id INTEGER REFERENCES mft_profiles(id) ON DELETE SET NULL,
    auto_generate_counter_arguments BOOLEAN DEFAULT TRUE,
    show_evidence BOOLEAN DEFAULT TRUE,
    show_critiques BOOLEAN DEFAULT TRUE,
    max_results INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Import logs for tracking XML imports
CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    argument_map_id INTEGER REFERENCES argument_maps(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    success BOOLEAN NOT NULL,
    message TEXT,
    error_details JSONB,
    import_type VARCHAR(50) DEFAULT 'xml',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
 

-- XML schema definitions - For managing validation schemas
CREATE TABLE xml_schema_definitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    schema_type VARCHAR(50) CHECK (schema_type IN ('XSD', 'SCHEMATRON')),
    schema_content TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, version, schema_type)
);
