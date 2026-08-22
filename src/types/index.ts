export interface Env {
    DB: D1Database;
    STORAGE: R2Bucket;
    JWT_SECRET: string;
    PUBLIC_R2_URL: string;
}

export interface User {
    id: string;
    username: string;
    password_hash: string;
    role: string;
    created_at: string;
}

export interface Pengumuman {
    id: string;
    title: string;
    slug: string;
    category: 'kegiatan' | 'oprec' | 'ultah' | 'lainnya';
    content: string;
    image_url: string | null;
    date_published: string;
    author: string;
    views: number;
    created_at: string;
    updated_at: string;
}

export interface Divisi {
    id: string;
    name: string;
    description: string | null;
    order_priority: number;
}

export interface Pengurus {
    id: string;
    divisi_id: string;
    name: string;
    role: string;
    photo_url: string | null;
    period: string;
    order_priority: number;
}

export interface FormLink {
    key: string;
    title: string;
    google_form_url: string;
    is_active: number;
    updated_at: string;
}
