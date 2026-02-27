# api/config/scoring_matrix.py

SCORING_MATRIX = {
    # Role ID 1: Data Engineer
    '1': {
        'weights': {
            '1': {'Q1': 0.30, 'Q2': 0.25, 'Q3': 0.15, 'Q4': 0.15, 'Q5': 0.15},
            '2': {'Q1': 0.20, 'Q2': 0.25, 'Q3': 0.20, 'Q4': 0.20, 'Q5': 0.15},
            '3': {'Q1': 0.15, 'Q2': 0.20, 'Q3': 0.15, 'Q4': 0.20, 'Q5': 0.30},
        },
        'rubrics': {
            '1': {
                'description': 'Fokus pada sintaks, konsep dasar yang akurat, dan langkah implementasi yang benar. Skor 100 diberikan jika jawaban berfungsi dan benar secara teknis.',
                'keywords': ['fungsi dasar', 'implementasi', 'langkah-langkah'],
            },
            '2': {
                'description': 'Fokus pada efisiensi, perbandingan solusi (trade-off sederhana), dan penerapan best practices. Skor 100 diberikan jika solusi optimal dan terjustifikasi.',
                'keywords': ['efisiensi', 'trade-off', 'best practices', 'optimal'],
            },
            '3': {
                'description': 'Fokus pada strategi, arsitektur skala besar, manajemen risiko, dan koneksi ke tujuan bisnis/skalabilitas. Skor 100 diberikan jika jawaban holistik dan visioner.',
                'keywords': ['arsitektur', 'skalabilitas', 'strategi', 'risiko', 'dampak bisnis'],
            },
        },
    },

    # Role ID 2: Data Scientist
    '2': {
        'weights': {
            '1': {'Q1': 0.30, 'Q2': 0.25, 'Q3': 0.15, 'Q4': 0.15, 'Q5': 0.15},
            '2': {'Q1': 0.20, 'Q2': 0.25, 'Q3': 0.20, 'Q4': 0.20, 'Q5': 0.15},
            '3': {'Q1': 0.15, 'Q2': 0.20, 'Q3': 0.15, 'Q4': 0.20, 'Q5': 0.30},
        },
        'rubrics': {
            '1': {
                'description': 'Fokus pada pemahaman algoritma dasar, preprocessing, dan validasi model.',
                'keywords': ['algoritma dasar', 'preprocessing', 'validasi'],
            },
            '2': {
                'description': 'Fokus pada tuning model, evaluasi mendalam, dan efisiensi komputasi.',
                'keywords': ['tuning', 'evaluasi', 'efisiensi'],
            },
            '3': {
                'description': 'Fokus pada desain sistem ML end-to-end, MLOps, dan dampak bisnis.',
                'keywords': ['MLOps', 'pipeline', 'strategi', 'dampak bisnis'],
            },
        },
    },

    # Role ID 3: Data Analyst
    '3': {
        'weights': {
            '1': {'Q1': 0.30, 'Q2': 0.25, 'Q3': 0.15, 'Q4': 0.15, 'Q5': 0.15},
            '2': {'Q1': 0.20, 'Q2': 0.25, 'Q3': 0.20, 'Q4': 0.20, 'Q5': 0.15},
            '3': {'Q1': 0.15, 'Q2': 0.20, 'Q3': 0.15, 'Q4': 0.20, 'Q5': 0.30},
        },
        'rubrics': {
            '1': {
                'description': 'Fokus pada SQL dasar, eksplorasi data, dan visualisasi dasar.',
                'keywords': ['SQL', 'EDA', 'visualisasi'],
            },
            '2': {
                'description': 'Fokus pada analitik mendalam, storytelling, dan efisiensi query.',
                'keywords': ['analitik', 'storytelling', 'efisiensi'],
            },
            '3': {
                'description': 'Fokus pada analisis strategis, otomatisasi dashboard, dan insight bisnis tingkat tinggi.',
                'keywords': ['strategi', 'otomatisasi', 'insight bisnis'],
            },
        },
    },

    # Role ID 4: Backend Developer
    '4': {
        'weights': {
            '1': {'Q1': 0.30, 'Q2': 0.25, 'Q3': 0.15, 'Q4': 0.15, 'Q5': 0.15},
            '2': {'Q1': 0.20, 'Q2': 0.25, 'Q3': 0.20, 'Q4': 0.20, 'Q5': 0.15},
            '3': {'Q1': 0.15, 'Q2': 0.20, 'Q3': 0.15, 'Q4': 0.20, 'Q5': 0.30},
        },
        'rubrics': {
            '1': {
                'description': 'Fokus pada sintaks API, CRUD dasar, dan koneksi database.',
                'keywords': ['API', 'CRUD', 'database'],
            },
            '2': {
                'description': 'Fokus pada efisiensi query, keamanan dasar, dan struktur kode.',
                'keywords': ['keamanan', 'efisiensi', 'clean code'],
            },
            '3': {
                'description': 'Fokus pada arsitektur microservices, skalabilitas, dan sistem terdistribusi.',
                'keywords': ['microservices', 'scalability', 'distributed system'],
            },
        },
    },

    # Role ID 5: Frontend Developer
    '5': {
        'weights': {
            '1': {'Q1': 0.30, 'Q2': 0.25, 'Q3': 0.15, 'Q4': 0.15, 'Q5': 0.15},
            '2': {'Q1': 0.20, 'Q2': 0.25, 'Q3': 0.20, 'Q4': 0.20, 'Q5': 0.15},
            '3': {'Q1': 0.15, 'Q2': 0.20, 'Q3': 0.15, 'Q4': 0.20, 'Q5': 0.30},
        },
        'rubrics': {
            '1': {
                'description': 'Fokus pada HTML/CSS dasar dan komponen UI dasar.',
                'keywords': ['HTML', 'CSS', 'UI'],
            },
            '2': {
                'description': 'Fokus pada SPA, state management, dan optimasi rendering.',
                'keywords': ['SPA', 'state', 'optimasi'],
            },
            '3': {
                'description': 'Fokus pada arsitektur frontend skala besar dan performa aplikasi.',
                'keywords': ['arsitektur', 'performa', 'scalability'],
            },
        },
    },

    # Role ID 6: Fullstack Developer
    '6': {
        'weights': {
            '1': {'Q1': 0.30, 'Q2': 0.25, 'Q3': 0.15, 'Q4': 0.15, 'Q5': 0.15},
            '2': {'Q1': 0.20, 'Q2': 0.25, 'Q3': 0.20, 'Q4': 0.20, 'Q5': 0.15},
            '3': {'Q1': 0.15, 'Q2': 0.20, 'Q3': 0.15, 'Q4': 0.20, 'Q5': 0.30},
        },
        'rubrics': {
            '1': {
                'description': 'Fokus pada fullstack dasar: API + UI.',
                'keywords': ['API', 'UI', 'dasar'],
            },
            '2': {
                'description': 'Fokus pada integrasi komponen, keamanan, dan optimasi.',
                'keywords': ['integrasi', 'keamanan', 'optimasi'],
            },
            '3': {
                'description': 'Fokus pada arsitektur end-to-end, DevOps dasar, dan skalabilitas.',
                'keywords': ['end-to-end', 'DevOps', 'skalabilitas'],
            },
        },
    },

    # Role ID 7: DevOps
    '7': {
        'weights': {
            '1': {'Q1': 0.30, 'Q2': 0.25, 'Q3': 0.15, 'Q4': 0.15, 'Q5': 0.15},
            '2': {'Q1': 0.20, 'Q2': 0.25, 'Q3': 0.20, 'Q4': 0.20, 'Q5': 0.15},
            '3': {'Q1': 0.15, 'Q2': 0.20, 'Q3': 0.15, 'Q4': 0.20, 'Q5': 0.30},
        },
        'rubrics': {
            '1': {
                'description': 'Fokus pada pipeline dasar, CI/CD, dan server dasar.',
                'keywords': ['CI/CD', 'server', 'pipeline'],
            },
            '2': {
                'description': 'Fokus pada container, monitoring, dan deployment otomatis.',
                'keywords': ['container', 'monitoring', 'deployment'],
            },
            '3': {
                'description': 'Fokus pada arsitektur DevOps skala besar, reliability, dan otomatisasi penuh.',
                'keywords': ['SRE', 'reliability', 'otomatisasi'],
            },
        },
    },

    # Role ID 8: Android Developer
    '8': {
        'weights': {
            '1': {'Q1': 0.30, 'Q2': 0.25, 'Q3': 0.15, 'Q4': 0.15, 'Q5': 0.15},
            '2': {'Q1': 0.20, 'Q2': 0.25, 'Q3': 0.20, 'Q4': 0.20, 'Q5': 0.15},
            '3': {'Q1': 0.15, 'Q2': 0.20, 'Q3': 0.15, 'Q4': 0.20, 'Q5': 0.30},
        },
        'rubrics': {
            '1': {
                'description': 'Fokus pada activity, layout, dan dasar Android.',
                'keywords': ['activity', 'layout', 'dasar'],
            },
            '2': {
                'description': 'Fokus pada MVVM, API integration, dan optimasi UI.',
                'keywords': ['MVVM', 'API', 'optimasi UI'],
            },
            '3': {
                'description': 'Fokus pada arsitektur Android skala besar dan performa aplikasi.',
                'keywords': ['arsitektur', 'performa', 'scalability'],
            },
        },
    },
}


def get_assessment_rubric(role_id: str, level_id: str):
    role_matrix = SCORING_MATRIX.get(role_id)
    if not role_matrix:
        return None
    return role_matrix['rubrics'].get(level_id)


def get_assessment_weights(role_id: str, level_id: str):
    role_matrix = SCORING_MATRIX.get(role_id)
    if not role_matrix:
        return None
    return role_matrix['weights'].get(level_id)
