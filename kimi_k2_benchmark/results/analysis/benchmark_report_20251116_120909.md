# Benchmark Results: Kimi K2 Thinking Comparison

**Generated**: 2025-11-16 12:09:09

---

## Summary
- Tested **3** model configurations, **2** were available
- **Best accuracy**: kimi_k2_via_make_it_heavy (82.7%)
- **Fastest response**: kimi_k2_direct (2.62s average)
- **Unavailable models**: qwen3_coder_30b
- **Make-it-heavy improvement**: +3.4% accuracy (but +5.7s latency)

## Model Comparison

| Model | Accuracy | Latency (s) | Tokens/s | Error Rate | Status |
| --- | --- | --- | --- | --- | --- |
| Kimi K2 Via Make It Heavy | 0.827 | 8.30 | 33.6 | 0.0% | available |
| Kimi K2 Direct | 0.794 | 2.62 | 139.0 | 0.0% | available |
| Qwen3 Coder 30B | 0.000 | 0.00 | 0.0 | 100.0% | unavailable |


## Detailed Metrics

### kimi_k2_via_make_it_heavy

- **status**: available
- **avg_accuracy**: 0.827
- **avg_latency**: 8.298
- **min_latency**: 6.137
- **max_latency**: 11.198
- **tokens_per_second**: 33.615
- **error_rate**: 0.000
- **total_runs**: 5
- **successful_runs**: 5
- **std_accuracy**: 0.090
- **std_latency**: 2.135

### kimi_k2_direct

- **status**: available
- **avg_accuracy**: 0.794
- **avg_latency**: 2.615
- **min_latency**: 1.711
- **max_latency**: 2.972
- **tokens_per_second**: 139.008
- **error_rate**: 0.000
- **total_runs**: 5
- **successful_runs**: 5
- **std_accuracy**: 0.074
- **std_latency**: 0.520

### qwen3_coder_30b

- **status**: unavailable
- **avg_accuracy**: 0.000
- **avg_latency**: 0.000
- **tokens_per_second**: 0.000
- **error_rate**: 1.000
- **total_runs**: 5

## Performance Visualization

### Avg Accuracy Comparison

```
kimi_k2_via_make_it_ ██████████████████████████████████████████████████ 0.827
kimi_k2_direct       ███████████████████████████████████████████████ 0.794
```

## Recommendations
### Kimi K2: Direct vs Make-it-heavy

- **Use direct mode** for most tasks (similar accuracy, 0.3x faster)
- Consider make-it-heavy only for tasks requiring multiple perspectives

### Local Model Setup
- **Qwen3-Coder:30B** was unavailable during testing
- To enable: Install Ollama and run `ollama pull qwen3-coder:30b`
- Local models can provide better latency and data privacy

### General Recommendations
- For **production use**: Choose based on latency requirements vs accuracy needs
- For **development**: Direct mode offers best balance of speed and quality
- For **complex reasoning**: Make-it-heavy may provide marginal improvements
