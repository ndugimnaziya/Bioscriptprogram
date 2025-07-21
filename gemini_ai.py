#!/usr/bin/env python3
"""
BioScript - Gemini AI İnteqrasiyası
Həkim köməkçisi və resept analiz sistemi
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# .env faylını yüklə
load_dotenv()

class BioScriptAI:
    """BioScript üçün Gemini AI köməkçisi"""
    
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable təyin edilməlidir")
        genai.configure(api_key=api_key)
        
    def analyze_patient_history(self, patient_data, prescriptions):
        """Xəstənin tarixçəsini analiz edir"""
        try:
            patient_info = f"""
            Xəstə: {patient_data.get('name', 'N/A')}
            FİN: {patient_data.get('fin_code', 'N/A')}
            Doğum tarixi: {patient_data.get('birth_date', 'N/A')}
            
            Əvvəlki reseptlər:
            """
            
            for prescription in prescriptions:
                patient_info += f"""
                Tarix: {prescription.get('issued_at', 'N/A')}
                Şikayət: {prescription.get('complaint', 'N/A')}
                Diaqnoz: {prescription.get('diagnosis', 'N/A')}
                Dərmanlar: {[med.get('name', 'N/A') for med in prescription.get('medications', [])]}
                """
            
            prompt = f"""
            Siz tibbi köməkçi süni intellektsiniz. Aşağıdakı xəstənin tibbi tarixini analiz edin və həkimə məsləhətlər verin:
            
            {patient_info}
            
            Lütfən:
            1. Xəstənin əsas problemlərini xülasə edin
            2. Dərman tarixindəki tendensiyaları qeyd edin
            3. Diqqət edilməli riskləri bildirin
            4. Həkimə tövsiyələr verin
            
            Cavabı Azərbaycan dilində, qısa və aydın verin.
            """
            
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            return response.text or "Analiz edilə bilmədi"
            
        except Exception as e:
            return f"Analiz xətası: {str(e)}"
    
    def get_treatment_suggestion(self, complaint, symptoms, patient_history=""):
        """Şikayət və simptomlara görə müalicə təklifi"""
        try:
            prompt = f"""
            Xəstənin şikayəti: {complaint}
            Simptomlar: {symptoms}
            Xəstənin tarixçəsi: {patient_history}
            
            Azərbaycan dilində həkim üçün qısa və praktik məsləhət verin:
            1. Ehtimal edilən diaqnozlar
            2. Tövsiyə edilən müayinələr
            3. Müalicə variantları
            4. Xəbərdarlıqlar
            """
            
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            return response.text or "Məsləhət alına bilmədi"
            
        except Exception as e:
            return f"Məsləhət xətası: {str(e)}"
    
    def chat_with_doctor(self, question, context=""):
        """Həkimlə söhbət"""
        try:
            prompt = f"""
            Siz BioScript sistemində həkim köməkçisi süni intellektsiniz. 
            Kontekst: {context}
            Həkimin sualı: {question}
            
            Azərbaycan dilində professional və faydalı cavab verin.
            """
            
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            return response.text or "Cavab alına bilmədi"
            
        except Exception as e:
            return f"Cavab xətası: {str(e)}"