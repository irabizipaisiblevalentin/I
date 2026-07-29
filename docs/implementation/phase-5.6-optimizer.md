# Phase 5.6: Optimizer Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Implement the optimizer that improves IR for better performance:

1. **Constant Folding**: Evaluate constant expressions at compile time
2. **Dead Code Elimination**: Remove unreachable code
3. **Inlining**: Inline small functions
4. **Escape Analysis**: Analyze variable escaping
5. **Loop Optimization**: Optimize loop structures
6. **Memory Optimization**: Reduce memory operations
7. **SSA**: Static Single Assignment form (when applicable)

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 90% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Optimization Effectiveness | > 30% | Code size reduction |
| Performance Improvement | > 20% | Execution speed |

### 1.3 Non-Objectives

- Code generation (Phase 5.7)
- Runtime optimization (VM phase)
- Profile-guided optimization (Future phase)

---

## 2. Engineering Design

### 2.1 Architecture Overview

```
Raw IR
    ↓
Optimization Passes
    ↓
    ├── Constant Folding
    ├── Dead Code Elimination
    ├── Inlining
    ├── Escape Analysis
    ├── Loop Optimization
    └── Memory Optimization
    ↓
Optimized IR
```

### 2.2 Optimization Passes

#### 2.2.1 Constant Folding

Evaluate constant expressions at compile time:

```
// Before
%0 = const 2
%1 = const 3
%2 = add %0, %1

// After
%0 = const 5
```

#### 2.2.2 Dead Code Elimination

Remove unreachable code:

```
// Before
%0 = const 1
ret %0
%1 = const 2  // Dead code

// After
%0 = const 1
ret %0
```

#### 2.2.3 Inlining

Inline small functions:

```
// Before
fn add(a: int, b: int) -> int {
    ret a + b
}
%0 = call add(1, 2)

// After
%0 = add 1, 2
```

#### 2.2.4 Escape Analysis

Analyze whether variables escape their scope:

```
// Before
%0 = alloca int
store %0, 42
%1 = load %0
ret %1

// After (if %0 doesn't escape)
%0 = const 42
ret %0
```

#### 2.2.5 Loop Optimization

Optimize loop structures:

```
// Before
loop:
    %0 = add %i, 1
    br loop

// After (strength reduction)
loop:
    %0 = add %i, 1
    br loop
```

#### 2.2.6 Memory Optimization

Reduce memory operations:

```
// Before
%0 = alloca int
store %0, 42
%1 = load %0

// After (store-to-load forwarding)
%0 = const 42
```

### 2.3 Pass Manager Design

```rust
// Pass manager
pub struct PassManager {
    passes: Vec<Box<dyn OptimizationPass>>,
    config: OptimizerConfig,
}

impl PassManager {
    pub fn new(config: OptimizerConfig) -> Self { ... }
    
    pub fn add_pass(&mut self, pass: Box<dyn OptimizationPass>) { ... }
    
    pub fn optimize(&mut self, module: &mut IrModule) -> Result<OptimizationStats, OptimizerError> {
        let mut stats = OptimizationStats::new();
        for pass in &mut self.passes {
            stats.merge(pass.run(module)?);
        }
        Ok(stats)
    }
}

// Optimization pass trait
pub trait OptimizationPass {
    fn name(&self) -> &str;
    fn run(&mut self, module: &mut IrModule) -> Result<OptimizationStats, OptimizerError>;
}
```

### 2.4 Optimization Levels

```rust
// Optimization levels
pub enum OptimizationLevel {
    None,       // -O0: No optimization
    Basic,      // -O1: Basic optimizations
    Standard,   // -O2: Standard optimizations
    Aggressive, // -O3: Aggressive optimizations
}

impl OptimizationLevel {
    pub fn passes(&self) -> Vec<Box<dyn OptimizationPass>> {
        match self {
            Self::None => vec![],
            Self::Basic => vec![
                Box::new(ConstantFolding),
                Box::new(DeadCodeElimination),
            ],
            Self::Standard => vec![
                Box::new(ConstantFolding),
                Box::new(DeadCodeElimination),
                Box::new(Inlining),
                Box::new(LoopOptimization),
            ],
            Self::Aggressive => vec![
                Box::new(ConstantFolding),
                Box::new(DeadCodeElimination),
                Box::new(Inlining),
                Box::new(EscapeAnalysis),
                Box::new(LoopOptimization),
                Box::new(MemoryOptimization),
            ],
        }
    }
}
```

### 2.5 Optimization Statistics

```rust
// Optimization statistics
pub struct OptimizationStats {
    pub constant_folds: usize,
    pub dead_code_eliminated: usize,
    pub functions_inlined: usize,
    pub loops_optimized: usize,
    pub memory_ops_reduced: usize,
    pub instructions_reduced: usize,
    pub code_size_before: usize,
    pub code_size_after: usize,
}

impl OptimizationStats {
    pub fn code_size_reduction(&self) -> f64 {
        (self.code_size_before - self.code_size_after) as f64 / self.code_size_before as f64
    }
}
```

---

## 3. File Structure

### 3.1 Crate Structure

```
crates/
└── ilang-optimizer/
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs
    │   ├── pass_manager.rs
    │   ├── constant_folding.rs
    │   ├── dead_code_elimination.rs
    │   ├── inlining.rs
    │   ├── escape_analysis.rs
    │   ├── loop_optimization.rs
    │   ├── memory_optimization.rs
    │   ├── ssa.rs
    │   ├── stats.rs
    │   └── error.rs
    └── tests/
        ├── constant_folding_tests.rs
        ├── dead_code_elimination_tests.rs
        ├── inlining_tests.rs
        ├── escape_analysis_tests.rs
        ├── loop_optimization_tests.rs
        ├── memory_optimization_tests.rs
        └── ssa_tests.rs
```

### 3.2 Key Files

```toml
# crates/ilang-optimizer/Cargo.toml
[package]
name = "ilang-optimizer"
version.workspace = true
edition.workspace = true

[dependencies]
ilang-core = { workspace = true }
ilang-ir = { workspace = true }
ilang-diagnostics = { workspace = true }
ilang-error = { workspace = true }
```

---

## 4. Implementation Plan

### 4.1 Implementation Order

| Step | Component | Dependencies | Estimate |
|------|-----------|--------------|----------|
| 1 | Pass manager | ilang-ir | 2 days |
| 2 | Constant folding | pass manager | 3 days |
| 3 | Dead code elimination | pass manager | 3 days |
| 4 | Inlining | pass manager | 3 days |
| 5 | Escape analysis | pass manager | 4 days |
| 6 | Loop optimization | pass manager | 3 days |
| 7 | Memory optimization | pass manager | 3 days |
| 8 | SSA (optional) | all above | 4 days |
| 9 | Statistics | all above | 2 days |
| 10 | Unit tests | all above | 4 days |
| 11 | Integration tests | all above | 3 days |
| 12 | Documentation | all above | 3 days |

**Total Estimated Duration:** 37 days (7 weeks)

### 4.2 Detailed Implementation Steps

#### Step 1: Pass Manager (2 days)

```rust
// crates/ilang-optimizer/src/pass_manager.rs

pub struct PassManager {
    passes: Vec<Box<dyn OptimizationPass>>,
    config: OptimizerConfig,
}

impl PassManager {
    pub fn new(config: OptimizerConfig) -> Self {
        let mut manager = Self {
            passes: Vec::new(),
            config,
        };
        manager.add_default_passes();
        manager
    }
    
    fn add_default_passes(&mut self) {
        match self.config.level {
            OptimizationLevel::None => {},
            OptimizationLevel::Basic => {
                self.add_pass(Box::new(ConstantFolding::new()));
                self.add_pass(Box::new(DeadCodeElimination::new()));
            },
            OptimizationLevel::Standard => {
                self.add_pass(Box::new(ConstantFolding::new()));
                self.add_pass(Box::new(DeadCodeElimination::new()));
                self.add_pass(Box::new(Inlining::new(self.config.inline_threshold)));
                self.add_pass(Box::new(LoopOptimization::new()));
            },
            OptimizationLevel::Aggressive => {
                self.add_pass(Box::new(ConstantFolding::new()));
                self.add_pass(Box::new(DeadCodeElimination::new()));
                self.add_pass(Box::new(Inlining::new(self.config.inline_threshold)));
                self.add_pass(Box::new(EscapeAnalysis::new()));
                self.add_pass(Box::new(LoopOptimization::new()));
                self.add_pass(Box::new(MemoryOptimization::new()));
            },
        }
    }
    
    pub fn optimize(&mut self, module: &mut IrModule) -> Result<OptimizationStats, OptimizerError> {
        let mut stats = OptimizationStats::new();
        for pass in &mut self.passes {
            stats.merge(pass.run(module)?);
        }
        Ok(stats)
    }
}
```

#### Step 2: Constant Folding (3 days)

```rust
// crates/ilang-optimizer/src/constant_folding.rs

pub struct ConstantFolding;

impl OptimizationPass for ConstantFolding {
    fn name(&self) -> &str {
        "constant_folding"
    }
    
    fn run(&mut self, module: &mut IrModule) -> Result<OptimizationStats, OptimizerError> {
        let mut stats = OptimizationStats::new();
        for function in &mut module.functions {
            for block in &mut function.basic_blocks {
                self.fold_block(block, &mut stats)?;
            }
        }
        Ok(stats)
    }
}

impl ConstantFolding {
    fn fold_block(&mut self, block: &mut BasicBlock, stats: &mut OptimizationStats) -> Result<(), OptimizerError> {
        let mut folded = Vec::new();
        for instruction in &block.instructions {
            match instruction {
                Instruction::Add(a, b, result) => {
                    if let (Some(a_val), Some(b_val)) = (self.get_const(*a), self.get_const(*b)) {
                        folded.push(Instruction::Const(*result, IrConst::Int(a_val + b_val)));
                        stats.constant_folds += 1;
                    } else {
                        folded.push(instruction.clone());
                    }
                },
                // ... more cases
                _ => folded.push(instruction.clone()),
            }
        }
        block.instructions = folded;
        Ok(())
    }
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.6.1 | Implement pass manager | Critical | 2 days | - |
| 5.6.2 | Implement constant folding | Critical | 3 days | 5.6.1 |
| 5.6.3 | Implement dead code elimination | Critical | 3 days | 5.6.1 |
| 5.6.4 | Implement inlining | High | 3 days | 5.6.1 |
| 5.6.5 | Implement escape analysis | High | 4 days | 5.6.1 |
| 5.6.6 | Implement loop optimization | High | 3 days | 5.6.1 |
| 5.6.7 | Implement memory optimization | High | 3 days | 5.6.1 |
| 5.6.8 | Implement SSA (optional) | Medium | 4 days | All above |
| 5.6.9 | Implement statistics | High | 2 days | All above |
| 5.6.10 | Write unit tests | Critical | 4 days | All above |
| 5.6.11 | Write integration tests | Critical | 3 days | All above |
| 5.6.12 | Write documentation | High | 3 days | All above |

**Total Estimated Duration:** 37 days (7 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.6.1 | Week 1 | 5.6.1 |
| M5.6.2 | Week 2-3 | 5.6.2, 5.6.3, 5.6.4 |
| M5.6.3 | Week 4-5 | 5.6.5, 5.6.6, 5.6.7 |
| M5.6.4 | Week 6-7 | 5.6.8, 5.6.9, 5.6.10, 5.6.11, 5.6.12 |

---

## 6. Testing Strategy

### 6.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Unit Tests | 90% | Individual pass tests |
| Integration Tests | 85% | Pass interaction tests |
| Optimization Tests | 90% | Optimization effect tests |
| Correctness Tests | 100% | Preserves semantics tests |

### 6.2 Test Examples

```rust
// Constant folding test
#[test]
fn test_constant_folding() {
    let ir = create_ir_with_constant_add();
    let mut optimizer = create_optimizer(OptimizationLevel::Basic);
    let stats = optimizer.optimize(&mut ir).unwrap();
    assert_eq!(stats.constant_folds, 1);
    assert!(has_constant_value(&ir, 5));
}

// Dead code elimination test
#[test]
fn test_dead_code_elimination() {
    let ir = create_ir_with_dead_code();
    let mut optimizer = create_optimizer(OptimizationLevel::Basic);
    let stats = optimizer.optimize(&mut ir).unwrap();
    assert!(stats.dead_code_eliminated > 0);
    assert!(!has_unreachable_code(&ir));
}

// Correctness test
#[test]
fn test_optimization_preserves_semantics() {
    let ir = create_complex_ir();
    let original_result = execute_ir(&ir);
    let mut optimizer = create_optimizer(OptimizationLevel::Aggressive);
    optimizer.optimize(&mut ir).unwrap();
    let optimized_result = execute_ir(&ir);
    assert_eq!(original_result, optimized_result);
}
```

---

## 7. Security Considerations

### 7.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Correctness | Optimizations preserve semantics | Property tests |
| Memory Safety | No unsafe code | Clippy audit |
| DoS Prevention | No exponential blowup | Timeouts |

---

## 8. Performance Considerations

### 8.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Optimization Speed | > 50K LOC/s | Throughput |
| Code Size Reduction | > 30% | Size comparison |
| Runtime Improvement | > 20% | Execution time |

### 8.2 Optimization Strategies

1. **Incremental Optimization**: Optimize only changed regions
2. **Parallel Optimization**: Optimize independent functions in parallel
3. **Caching**: Cache optimization results
4. **Early Termination**: Stop when no more optimizations apply

---

## 9. Documentation Requirements

### 9.1 Documentation Types

| Type | Location | Audience |
|------|----------|----------|
| API Documentation | Source code | Developers |
| Optimization Guide | docs/optimization.md | Contributors |
| Pass Reference | docs/passes.md | Contributors |

---

## 10. Definition of Done

### 10.1 Phase 5.6 is complete when:

- [ ] All components implemented and compiling
- [ ] Unit tests passing (> 90% coverage)
- [ ] Integration tests passing
- [ ] Constant folding working
- [ ] Dead code elimination working
- [ ] Inlining working
- [ ] Documentation complete
- [ ] Examples working
- [ ] Cross-platform testing passing
- [ ] Security review complete
- [ ] Performance review complete
- [ ] Code review complete
- [ ] Changelog updated

### 10.2 Quality Gates

| Gate | Requirement | Status |
|------|-------------|--------|
| Build | Clean build passes | - |
| Tests | All tests pass | - |
| Coverage | > 90% | - |
| Lint | No warnings | - |
| Format | Formatted | - |
| Docs | All public API documented | - |
| Security | No vulnerabilities | - |
| Review | Code reviewed | - |

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
