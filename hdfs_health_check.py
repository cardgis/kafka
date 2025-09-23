#!/usr/bin/env python3
"""
HDFS Health Check - Exercise 7 Diagnostic
Vérifie que le système de stockage HDFS fonctionne correctement
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class HDFSHealthCheck:
    def __init__(self, hdfs_root='hdfs-data'):
        self.hdfs_root = Path(hdfs_root)
        self.issues = []
        self.stats = defaultdict(int)
    
    def run_full_diagnostic(self):
        """Exécute un diagnostic complet du système HDFS"""
        print("🔍 HDFS HEALTH CHECK - DIAGNOSTIC COMPLET")
        print("=" * 60)
        
        # Test 1: Vérification de l'existence du répertoire
        self.check_directory_exists()
        
        # Test 2: Vérification des permissions
        self.check_permissions()
        
        # Test 3: Analyse des fichiers
        self.analyze_files()
        
        # Test 4: Vérification de l'intégrité des données
        self.check_data_integrity()
        
        # Test 5: Analyse temporelle
        self.analyze_temporal_distribution()
        
        # Test 6: Vérification des alertes
        self.verify_alert_logic()
        
        # Rapport final
        self.generate_health_report()
    
    def check_directory_exists(self):
        """Test 1: Vérification de l'existence du répertoire HDFS"""
        print("\n📁 TEST 1: Structure de répertoires")
        print("-" * 40)
        
        if not self.hdfs_root.exists():
            self.issues.append("❌ Répertoire HDFS racine inexistant")
            print(f"❌ {self.hdfs_root.absolute()} n'existe pas")
            return False
        
        print(f"✅ Répertoire racine: {self.hdfs_root.absolute()}")
        
        # Compter les sous-répertoires
        countries = list(self.hdfs_root.iterdir())
        self.stats['countries'] = len([d for d in countries if d.is_dir()])
        
        total_cities = 0
        for country in countries:
            if country.is_dir():
                cities = list(country.iterdir())
                cities_count = len([d for d in cities if d.is_dir()])
                total_cities += cities_count
                print(f"  📍 {country.name}: {cities_count} villes")
        
        self.stats['cities'] = total_cities
        print(f"✅ Total: {self.stats['countries']} pays, {self.stats['cities']} villes")
        return True
    
    def check_permissions(self):
        """Test 2: Vérification des permissions d'écriture"""
        print("\n🔐 TEST 2: Permissions d'écriture")
        print("-" * 40)
        
        try:
            test_file = self.hdfs_root / "test_write.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            test_file.unlink()
            print("✅ Permissions d'écriture OK")
            return True
        except Exception as e:
            self.issues.append(f"❌ Problème de permissions: {e}")
            print(f"❌ Erreur de permissions: {e}")
            return False
    
    def analyze_files(self):
        """Test 3: Analyse des fichiers stockés"""
        print("\n📄 TEST 3: Analyse des fichiers")
        print("-" * 40)
        
        if not self.hdfs_root.exists():
            return False
        
        json_files = list(self.hdfs_root.rglob("*.json"))
        self.stats['total_files'] = len(json_files)
        
        if len(json_files) == 0:
            self.issues.append("⚠️ Aucun fichier JSON trouvé")
            print("⚠️ Aucun fichier d'alerte trouvé")
            return False
        
        print(f"✅ {len(json_files)} fichiers d'alerte trouvés")
        
        # Analyse de la taille des fichiers
        sizes = [f.stat().st_size for f in json_files]
        avg_size = sum(sizes) / len(sizes)
        min_size = min(sizes)
        max_size = max(sizes)
        
        print(f"📊 Tailles: min={min_size}B, max={max_size}B, moy={avg_size:.1f}B")
        
        # Vérifier les fichiers anormalement petits ou grands
        if min_size < 100:
            self.issues.append("⚠️ Fichiers très petits détectés (possibles erreurs)")
        if max_size > 10000:
            self.issues.append("⚠️ Fichiers très gros détectés")
        
        return True
    
    def check_data_integrity(self):
        """Test 4: Vérification de l'intégrité des données JSON"""
        print("\n🔍 TEST 4: Intégrité des données")
        print("-" * 40)
        
        json_files = list(self.hdfs_root.rglob("*.json"))
        valid_files = 0
        corrupt_files = 0
        
        sample_data = []
        
        for i, file_path in enumerate(json_files[:10]):  # Test sur 10 fichiers
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Vérifier la structure attendue
                if self.validate_json_structure(data):
                    valid_files += 1
                    if len(sample_data) < 3:
                        sample_data.append(data)
                else:
                    self.issues.append(f"⚠️ Structure invalide: {file_path.name}")
                    
            except json.JSONDecodeError as e:
                corrupt_files += 1
                self.issues.append(f"❌ JSON corrompu: {file_path.name}")
            except Exception as e:
                corrupt_files += 1
                self.issues.append(f"❌ Erreur lecture: {file_path.name} - {e}")
        
        print(f"✅ {valid_files}/10 fichiers testés sont valides")
        if corrupt_files > 0:
            print(f"❌ {corrupt_files} fichiers corrompus détectés")
        
        # Afficher un échantillon
        if sample_data:
            print("\n📋 Échantillon de données:")
            sample = sample_data[0]
            message = sample.get('message', {})
            print(f"  🌡️  Température: {message.get('temperature', 'N/A')}°C")
            print(f"  💨 Vent: {message.get('windspeed', 'N/A')} m/s")
            print(f"  🚨 Alertes: Wind={message.get('wind_alert_level', 'N/A')}, Heat={message.get('heat_alert_level', 'N/A')}")
        
        return corrupt_files == 0
    
    def validate_json_structure(self, data):
        """Valide la structure d'un fichier JSON d'alerte"""
        required_fields = ['stored_at', 'storage_path', 'message']
        
        # Vérifier les champs racine
        for field in required_fields:
            if field not in data:
                return False
        
        # Vérifier le message
        message = data.get('message', {})
        message_fields = ['latitude', 'longitude', 'temperature', 'windspeed']
        
        for field in message_fields:
            if field not in message:
                return False
        
        return True
    
    def analyze_temporal_distribution(self):
        """Test 5: Analyse de la distribution temporelle"""
        print("\n⏰ TEST 5: Distribution temporelle")
        print("-" * 40)
        
        json_files = list(self.hdfs_root.rglob("*.json"))
        
        if not json_files:
            return False
        
        # Analyser les timestamps de création des fichiers
        file_times = []
        for file_path in json_files:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            file_times.append(mtime)
        
        file_times.sort()
        
        if file_times:
            earliest = file_times[0]
            latest = file_times[-1]
            duration = latest - earliest
            
            print(f"📅 Premier fichier: {earliest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📅 Dernier fichier: {latest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  Période couverte: {duration}")
            
            # Vérifier s'il y a eu de l'activité récente (dernières 2 heures)
            now = datetime.now()
            recent_files = [t for t in file_times if now - t < timedelta(hours=2)]
            
            print(f"🕐 Fichiers récents (2h): {len(recent_files)}")
            
            if len(recent_files) == 0:
                self.issues.append("⚠️ Aucune activité récente détectée")
            else:
                print("✅ Système actif récemment")
        
        return True
    
    def verify_alert_logic(self):
        """Test 6: Vérification de la logique des alertes"""
        print("\n🚨 TEST 6: Logique des alertes")
        print("-" * 40)
        
        json_files = list(self.hdfs_root.rglob("*.json"))
        alert_stats = defaultdict(int)
        invalid_alerts = 0
        
        for file_path in json_files[:20]:  # Test sur 20 fichiers
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                message = data.get('message', {})
                temp = message.get('temperature')
                wind = message.get('windspeed')
                wind_alert = message.get('wind_alert_level', 'level_0')
                heat_alert = message.get('heat_alert_level', 'level_0')
                
                # Compter les types d'alertes
                alert_stats[f"wind_{wind_alert}"] += 1
                alert_stats[f"heat_{heat_alert}"] += 1
                
                # Vérifier la cohérence
                if temp is not None and heat_alert != 'level_0':
                    if heat_alert == 'level_1' and temp < 25:
                        invalid_alerts += 1
                    elif heat_alert == 'level_2' and temp < 35:
                        invalid_alerts += 1
                
                if wind is not None and wind_alert != 'level_0':
                    if wind_alert == 'level_1' and wind < 10:
                        invalid_alerts += 1
                    elif wind_alert == 'level_2' and wind < 20:
                        invalid_alerts += 1
                        
            except Exception:
                continue
        
        print("📊 Distribution des alertes:")
        for alert_type, count in sorted(alert_stats.items()):
            print(f"  {alert_type}: {count}")
        
        if invalid_alerts > 0:
            self.issues.append(f"⚠️ {invalid_alerts} alertes incohérentes détectées")
            print(f"⚠️ {invalid_alerts} alertes avec logique incohérente")
        else:
            print("✅ Logique des alertes cohérente")
        
        return invalid_alerts == 0
    
    def generate_health_report(self):
        """Génère le rapport final de santé du système"""
        print("\n" + "=" * 60)
        print("📋 RAPPORT DE SANTÉ HDFS")
        print("=" * 60)
        
        # Statut global
        if len(self.issues) == 0:
            print("🟢 STATUT: EXCELLENT - Système HDFS entièrement fonctionnel")
        elif len(self.issues) <= 2:
            print("🟡 STATUT: BON - Quelques avertissements mineurs")
        else:
            print("🔴 STATUT: PROBLÈMES - Action requise")
        
        # Statistiques
        print(f"\n📊 STATISTIQUES:")
        print(f"   • Pays stockés: {self.stats.get('countries', 0)}")
        print(f"   • Villes avec alertes: {self.stats.get('cities', 0)}")
        print(f"   • Total fichiers d'alerte: {self.stats.get('total_files', 0)}")
        
        # Problèmes détectés
        if self.issues:
            print(f"\n⚠️  PROBLÈMES DÉTECTÉS ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n✅ AUCUN PROBLÈME DÉTECTÉ")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        if len(self.issues) == 0:
            print("   • Système optimal - continuer la surveillance")
            print("   • Considérer un nettoyage périodique des anciens fichiers")
        else:
            print("   • Examiner et corriger les problèmes listés")
            print("   • Relancer le diagnostic après corrections")
        
        print("\n" + "=" * 60)

def main():
    checker = HDFSHealthCheck()
    checker.run_full_diagnostic()

if __name__ == "__main__":
    main()