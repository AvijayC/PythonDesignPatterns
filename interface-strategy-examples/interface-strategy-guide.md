# Interface and Strategy Pattern Implementation Guide

## Understanding Interfaces vs Concrete Implementations

### The Problem: Tight Coupling
```python
# BAD: Directly coupled to specific implementations
class DataProcessor:
    def __init__(self, file_type):
        self.file_type = file_type
    
    def process_data(self, data):
        if self.file_type == "csv":
            # CSV processing logic here
            return data.split(",")
        elif self.file_type == "json":
            # JSON processing logic here
            import json
            return json.loads(data)
        elif self.file_type == "xml":
            # XML processing logic here
            import xml.etree.ElementTree as ET
            return ET.fromstring(data)
        else:
            raise ValueError("Unsupported file type")
```

**Problems with this approach:**
- Violates Open/Closed Principle (must modify class to add new formats)
- Single Responsibility Principle violation (one class handles all formats)
- Hard to test individual format handlers
- Tight coupling between processor and specific implementations

## Solution: Interface + Strategy Pattern

### Step 1: Define the Interface
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class DataParserInterface(ABC):
    """Abstract interface for data parsing strategies"""
    
    @abstractmethod
    def parse(self, raw_data: str) -> Dict[str, Any]:
        """Parse raw data into structured format"""
        pass
    
    @abstractmethod
    def validate(self, data: str) -> bool:
        """Validate if data format is supported"""
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> list:
        """Return list of supported file extensions"""
        pass
```

### Step 2: Implement Concrete Strategies
```python
import json
import csv
import xml.etree.ElementTree as ET
from io import StringIO

class CSVParser(DataParserInterface):
    """Concrete strategy for CSV parsing"""
    
    def parse(self, raw_data: str) -> Dict[str, Any]:
        reader = csv.DictReader(StringIO(raw_data))
        return {"rows": list(reader), "format": "csv"}
    
    def validate(self, data: str) -> bool:
        try:
            # Simple validation - check if it contains commas
            return "," in data and len(data.split('\n')) > 0
        except Exception:
            return False
    
    @property
    def supported_extensions(self) -> list:
        return [".csv", ".txt"]

class JSONParser(DataParserInterface):
    """Concrete strategy for JSON parsing"""
    
    def parse(self, raw_data: str) -> Dict[str, Any]:
        parsed = json.loads(raw_data)
        return {"data": parsed, "format": "json"}
    
    def validate(self, data: str) -> bool:
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False
    
    @property
    def supported_extensions(self) -> list:
        return [".json", ".jsonl"]

class XMLParser(DataParserInterface):
    """Concrete strategy for XML parsing"""
    
    def parse(self, raw_data: str) -> Dict[str, Any]:
        root = ET.fromstring(raw_data)
        return {
            "root_tag": root.tag,
            "data": self._xml_to_dict(root),
            "format": "xml"
        }
    
    def validate(self, data: str) -> bool:
        try:
            ET.fromstring(data)
            return True
        except ET.ParseError:
            return False
    
    @property
    def supported_extensions(self) -> list:
        return [".xml", ".xaml"]
    
    def _xml_to_dict(self, element) -> Dict:
        """Helper method to convert XML to dict"""
        result = {}
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
```

### Step 3: Context Class Using Strategy Pattern
```python
from typing import Optional

class DataProcessor:
    """Context class that uses parsing strategies"""
    
    def __init__(self, parser: Optional[DataParserInterface] = None):
        self._parser = parser
        self._available_parsers = {
            'csv': CSVParser(),
            'json': JSONParser(),
            'xml': XMLParser()
        }
    
    def set_parser(self, parser: DataParserInterface) -> None:
        """Strategy setter - allows runtime strategy switching"""
        self._parser = parser
    
    def auto_detect_parser(self, data: str, filename: str = "") -> bool:
        """Automatically detect and set appropriate parser"""
        # Try to detect by file extension first
        if filename:
            extension = filename.lower().split('.')[-1]
            for parser_name, parser in self._available_parsers.items():
                if f".{extension}" in parser.supported_extensions:
                    self._parser = parser
                    return True
        
        # Fall back to content-based detection
        for parser in self._available_parsers.values():
            if parser.validate(data):
                self._parser = parser
                return True
        
        return False
    
    def process(self, raw_data: str, filename: str = "") -> Dict[str, Any]:
        """Main processing method"""
        # Auto-detect parser if none set
        if not self._parser:
            if not self.auto_detect_parser(raw_data, filename):
                raise ValueError("No suitable parser found for the data")
        
        # Validate data with current parser
        if not self._parser.validate(raw_data):
            raise ValueError(f"Data validation failed for {type(self._parser).__name__}")
        
        # Parse and return results
        result = self._parser.parse(raw_data)
        result['parser_used'] = type(self._parser).__name__
        return result
    
    def get_supported_formats(self) -> Dict[str, list]:
        """Return all supported formats"""
        return {
            parser_name: parser.supported_extensions 
            for parser_name, parser in self._available_parsers.items()
        }
```

### Step 4: Usage Examples
```python
# Example 1: Explicit strategy setting
processor = DataProcessor()
processor.set_parser(JSONParser())

json_data = '{"name": "John", "age": 30}'
result = processor.process(json_data)
print(result)  # {'data': {'name': 'John', 'age': 30}, 'format': 'json', 'parser_used': 'JSONParser'}

# Example 2: Auto-detection by filename
processor = DataProcessor()
csv_data = "name,age\nJohn,30\nJane,25"
result = processor.process(csv_data, "users.csv")
print(result)  # {'rows': [{'name': 'John', 'age': '30'}, {'name': 'Jane', 'age': '25'}], 'format': 'csv', 'parser_used': 'CSVParser'}

# Example 3: Runtime strategy switching
processor = DataProcessor(CSVParser())
print("CSV result:", processor.process(csv_data))

processor.set_parser(JSONParser())  # Switch strategies
print("JSON result:", processor.process(json_data))

# Example 4: Checking supported formats
print("Supported formats:", processor.get_supported_formats())
```

## Key Benefits of This Pattern

### 1. Open/Closed Principle
- **Open for extension**: Add new parsers without modifying existing code
- **Closed for modification**: Core `DataProcessor` doesn't need changes

### 2. Single Responsibility
- Each parser handles one specific format
- `DataProcessor` focuses on orchestration, not implementation details

### 3. Dependency Inversion
- High-level `DataProcessor` depends on abstraction (`DataParserInterface`)
- Not dependent on concrete implementations

### 4. Runtime Flexibility
- Switch parsing strategies at runtime
- Auto-detection capabilities
- Easy to test individual components

## Adding New Strategies
```python
class YAMLParser(DataParserInterface):
    """New strategy - no existing code modification needed"""
    
    def parse(self, raw_data: str) -> Dict[str, Any]:
        import yaml
        parsed = yaml.safe_load(raw_data)
        return {"data": parsed, "format": "yaml"}
    
    def validate(self, data: str) -> bool:
        try:
            import yaml
            yaml.safe_load(data)
            return True
        except yaml.YAMLError:
            return False
    
    @property
    def supported_extensions(self) -> list:
        return [".yaml", ".yml"]

# Register the new parser
processor = DataProcessor()
processor._available_parsers['yaml'] = YAMLParser()
```

## Real-World Applications

### Databricks Context
```python
# In Databricks notebook
from pyspark.sql import SparkSession

class SparkDataProcessor(DataProcessor):
    """Extended processor for Spark DataFrames"""
    
    def __init__(self, spark: SparkSession):
        super().__init__()
        self.spark = spark
    
    def process_to_dataframe(self, raw_data: str, filename: str = ""):
        """Process and convert to Spark DataFrame"""
        parsed_result = self.process(raw_data, filename)
        
        if parsed_result['format'] == 'json':
            # Convert JSON to Spark DataFrame
            rdd = self.spark.sparkContext.parallelize([parsed_result['data']])
            return self.spark.read.json(rdd)
        elif parsed_result['format'] == 'csv':
            # Convert CSV to Spark DataFrame
            rows = parsed_result['rows']
            if rows:
                return self.spark.createDataFrame(rows)
        
        return None

# Usage in Databricks
spark = SparkSession.builder.getOrCreate()
processor = SparkDataProcessor(spark)
df = processor.process_to_dataframe(csv_data, "data.csv")
df.show()
```

This pattern is fundamental to building maintainable, extensible data processing pipelines in enterprise environments.