
import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, ScrollView } from 'react-native';
import axios from 'axios';

export default function ChatScreen({ navigation }) {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');

  const handleSend = async () => {
    try {
      const res = await axios.post('http://localhost:3001/chat', { message }, {
        headers: { 'x-user-id': 'tauros' }
      });
      setResponse(res.data.response);
    } catch (e) {
      setResponse('Errore nel contatto con Tauros.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>TAUROS</Text>
      <ScrollView style={styles.responseBox}>
        <Text style={styles.responseText}>{response}</Text>
      </ScrollView>
      <TextInput
        style={styles.input}
        placeholder="Scrivi qui..."
        value={message}
        onChangeText={setMessage}
      />
      <Button title="Invia" onPress={handleSend} />
      <Button title="Impostazioni" onPress={() => navigation.navigate('Settings')} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', padding: 20 },
  title: { fontSize: 28, color: '#33cc99', marginBottom: 10, textAlign: 'center', fontWeight: 'bold' },
  responseBox: { flex: 1, marginVertical: 10 },
  responseText: { color: '#fff', fontSize: 16 },
  input: { backgroundColor: '#1a1a1a', color: '#f0f0f0', padding: 10, marginBottom: 10, borderRadius: 8 }
});
