
import React, { useState } from 'react';
import { View, Text, Switch, StyleSheet } from 'react-native';

export default function SettingsScreen() {
  const [gptMode, setGptMode] = useState(true);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Impostazioni</Text>
      <View style={styles.option}>
        <Text style={styles.label}>GPT Mode</Text>
        <Switch value={gptMode} onValueChange={setGptMode} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', padding: 24 },
  title: { fontSize: 24, color: '#33cc99', marginBottom: 20 },
  option: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  label: { color: '#fff', fontSize: 18 }
});
