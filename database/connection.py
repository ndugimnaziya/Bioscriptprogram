#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import os
from dotenv import load_dotenv

# .env faylından dəyərləri yüklə
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER') 
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        self.connection = None
        
    def connect(self):
        """MySQL verilənlər bazasına qoşul"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return True
        except Exception as e:
            print(f"Verilənlər bazası qoşulma xətası: {e}")
            return False
    
    def disconnect(self):
        """Bağlantını kəs"""
        if self.connection and not self.connection._closed:
            try:
                self.connection.close()
            except Exception:
                pass  # Artıq bağlıdırsa xəta yaranmaz
    
    def execute_query(self, query, params=None):
        """SQL sorğusunu icra et"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Sorğu xətası: {e}")
            return None
            
    def execute_insert(self, query, params=None):
        """INSERT sorğusunu icra et və ID qaytır"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.lastrowid
        except Exception as e:
            print(f"INSERT xətası: {e}")
            return None