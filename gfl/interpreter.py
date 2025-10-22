import logging

from gfl.plugins.plugin_registry import plugin_registry

logger = logging.getLogger(__name__)


class Interpreter:
    """Lightweight AST walker with optional plugin invocation support."""

    def __init__(self):
        self.symbol_table = {}

    def interpret(self, ast):
        """Entry point to interpret a program AST."""
        self.visit(ast)

    def visit(self, node):
        """Dynamic dispatch for AST node handlers."""
        if not isinstance(node, dict):
            logger.warning(f"Invalid AST node encountered: {node}")
            return

        # Handle YAML structure for spatial genomic features
        if "loci" in node:
            self.visit_loci_statement({"node_type": "loci", "loci": node["loci"]})
        if "rules" in node:
            self.visit_rules_statement({"node_type": "rules", "rules": node["rules"]})
        if "simulate" in node:
            self.visit_simulate_statement({"node_type": "simulate", "properties": node["simulate"]})

        # Handle traditional AST nodes
        if "type" in node:
            method_name = f"visit_{node['type']}"
            visitor_method = getattr(self, method_name, self.generic_visit)
            return visitor_method(node)

    def generic_visit(self, node):
        """Default visit: walk nested dict/list children."""
        for _, value in node.items():
            if isinstance(value, dict) and "type" in value:
                self.visit(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "type" in item:
                        self.visit(item)

    def visit_program(self, node):
        for statement in node.get("body", []):
            self.visit(statement)

    def visit_define_statement(self, node):
        var_name = node["name"]
        value = self.evaluate_expression(node.get("value"))
        self.symbol_table[var_name] = value
        logger.info(f"DEFINED: {var_name} = {value}")

    def visit_invoke_statement(self, node):
        plugin_name = node["plugin"]
        method_name = node["method"]
        params = {k: self.evaluate_expression(v) for k, v in node.get("params", {}).items()}

        as_var = node.get("as_var")
        try:
            plugin = plugin_registry.get(plugin_name)
            result = plugin.execute(method_name, params, self.symbol_table)
            if as_var:
                self.symbol_table[as_var] = result
                logger.info(f"INVOKED: {plugin_name}.{method_name} (stored in {as_var})")
            else:
                logger.info(f"INVOKED: {plugin_name}.{method_name}")
            return result
        except Exception as e:
            logger.error(
                f"Error executing plugin {plugin_name}.{method_name}: {e}",
                exc_info=True,
            )
            raise

    def visit_message_statement(self, node):
        message_value = self.evaluate_expression(node["message"])
        logger.info(f"MESSAGE: {message_value}")

    def visit_branch_statement(self, node):
        condition_result = self.evaluate_expression(node["condition"])
        if condition_result:
            logger.info("BRANCH: Condition true, executing THEN branch.")
            self.visit(node["then_branch"])
        elif "else_branch" in node:
            logger.info("BRANCH: Condition false, executing ELSE branch.")
            self.visit(node["else_branch"])
        else:
            logger.info("BRANCH: Condition false, no ELSE branch.")

    def visit_try_catch_statement(self, node):
        logger.info("Entering TRY block...")
        try:
            self.visit(node["try_block"])
            logger.info("TRY block completed successfully.")
        except Exception as e:
            logger.info(f"Caught exception: {e}. Executing CATCH block...")
            self.symbol_table["__last_error__"] = str(e)
            self.visit(node["catch_block"])
            logger.info("CATCH block completed.")

    def visit_loci_statement(self, node):
        """Handle loci definitions for genomic coordinates."""
        logger.info("Processing LOCI definitions...")
        loci_data = node.get("loci", [])
        for locus in loci_data:
            locus_id = locus.get("id")
            chromosome = locus.get("chromosome")
            start = locus.get("start")
            end = locus.get("end")
            elements = locus.get("elements", [])
            haplotype_panel = locus.get("haplotype_panel")

            # Store locus information in symbol table
            self.symbol_table[locus_id] = {
                "type": "locus",
                "chromosome": chromosome,
                "start": start,
                "end": end,
                "elements": elements,
                "haplotype_panel": haplotype_panel,
            }
            logger.info(f"Defined locus {locus_id}: {chromosome}:{start}-{end}")
            if haplotype_panel:
                logger.info(f"  Haplotype panel: {haplotype_panel}")

    def visit_rules_statement(self, node):
        """Handle rules with spatial predicates."""
        logger.info("Processing RULES definitions...")
        rules_data = node.get("rules", [])
        for rule in rules_data:
            rule_id = rule.get("id")
            description = rule.get("description")
            if_condition = rule.get("if")
            then_actions = rule.get("then", [])

            # Store rule in symbol table
            self.symbol_table[rule_id] = {
                "type": "rule",
                "description": description,
                "if": if_condition,
                "then": then_actions,
            }
            logger.info(f"Defined rule {rule_id}: {description}")

    def evaluate_spatial_condition(self, condition):
        """Evaluate spatial genomic conditions."""
        if not condition:
            return False

        # Handle list of conditions (AND logic)
        if isinstance(condition, list):
            return all(self.evaluate_spatial_condition(c) for c in condition)

        condition_type = condition.get("type")

        if condition_type == "is_within":
            element = condition.get("element")
            locus = condition.get("locus")
            return self._check_is_within(element, locus)

        elif condition_type == "distance_between":
            element_a = condition.get("element_a")
            element_b = condition.get("element_b")
            threshold = condition.get("threshold", 0)
            distance = self._calculate_distance(element_a, element_b)
            return distance > threshold

        elif condition_type == "is_in_contact":
            element_a = condition.get("element_a")
            element_b = condition.get("element_b")
            hic_map = condition.get("hic_map")
            return self._check_is_in_contact(element_a, element_b, hic_map)

        elif condition_type == "not":
            return not self.evaluate_spatial_condition(condition.get("condition"))

        elif condition_type == "logical":
            operator = condition.get("operator")
            left = self.evaluate_spatial_condition(condition.get("left"))
            right = self.evaluate_spatial_condition(condition.get("right"))

            if operator == "and":
                return left and right
            elif operator == "or":
                return left or right

        return False

    def _check_is_within(self, element, locus):
        """Check if an element is within a genomic locus."""
        if element not in self.symbol_table or locus not in self.symbol_table:
            return False

        element_data = self.symbol_table[element]
        locus_data = self.symbol_table[locus]

        if locus_data.get("type") != "locus":
            return False

        # For now, assume elements have coordinates stored
        # In a real implementation, you'd look up element coordinates
        element_start = element_data.get("start", 0)
        element_end = element_data.get("end", 0)
        locus_start = locus_data.get("start", 0)
        locus_end = locus_data.get("end", 0)

        return locus_start <= element_start and element_end <= locus_end

    def _calculate_distance(self, element_a, element_b):
        """Calculate distance between two genomic elements."""
        if element_a not in self.symbol_table or element_b not in self.symbol_table:
            return float("inf")

        element_a_data = self.symbol_table[element_a]
        element_b_data = self.symbol_table[element_b]

        # For now, return a mock distance calculation
        # In a real implementation, you'd calculate actual genomic distance
        return abs(element_a_data.get("start", 0) - element_b_data.get("start", 0))

    def _check_is_in_contact(self, element_a, element_b, hic_map):
        """Check if two elements are in 3D contact using Hi-C data."""
        # This is a placeholder for Hi-C contact analysis
        # In a real implementation, you'd load and query Hi-C data
        logger.info(f"Checking 3D contact between {element_a} and {element_b} using {hic_map}")
        return True  # Placeholder return

    def visit_simulate_statement(self, node):
        """Handle enhanced simulate statements for spatial genomic reasoning."""
        logger.info("Processing SIMULATE statement...")

        # Handle different simulate statement formats
        if "target" in node:
            # Legacy format: SIMULATE target
            target = node["target"]
            logger.info(f"Simulating target: {target}")
            return

        # Enhanced format with properties
        properties = node.get("properties", {})
        simulation_name = properties.get("name", "unnamed_simulation")
        action = properties.get("action")
        queries = properties.get("query", [])
        description = properties.get("description", "")

        logger.info(f"Running simulation: {simulation_name}")
        if description:
            logger.info(f"Description: {description}")

        # Execute the hypothetical action
        if action:
            self._execute_simulation_action(action)

        # Evaluate queries based on rules
        results = {}
        for query in queries:
            query_result = self._evaluate_simulation_query(query)
            results[query.get("element", "unknown")] = query_result

        logger.info(f"Simulation results: {results}")
        return results

    def _execute_simulation_action(self, action):
        """Execute a hypothetical action for simulation."""
        action_type = action.get("type")

        if action_type == "move":
            element = action.get("element")
            destination = action.get("destination")
            logger.info(f"Simulating move of {element} to {destination}")
            # In a real implementation, you'd update the element's coordinates
            # and store the change in a simulation context

        elif action_type == "set_activity":
            element = action.get("element")
            level = action.get("level")
            logger.info(f"Simulating activity change: {element} -> {level}")
            # Store the simulated activity change

    def _evaluate_simulation_query(self, query):
        """Evaluate a query in the context of the simulation."""
        query_type = query.get("type")

        if query_type == "get_activity":
            element = query.get("element")
            level = query.get("level", "any")

            # Apply rules to determine activity based on spatial conditions
            activity = self._determine_activity_from_rules(element, level)
            logger.info(f"Query result: {element} activity = {activity}")
            return activity

        return None

    def _determine_activity_from_rules(self, element, level):
        """Determine element activity by applying spatial rules."""
        # Find all rules that might affect this element
        applicable_rules = []
        for value in self.symbol_table.values():
            if isinstance(value, dict) and value.get("type") == "rule":
                rule_condition = value.get("if")
                if self._rule_applies_to_element(rule_condition, element):
                    applicable_rules.append(value)

        # Apply rules to determine activity
        for rule in applicable_rules:
            if self.evaluate_spatial_condition(rule.get("if")):
                actions = rule.get("then", [])
                for action in actions:
                    if action.get("type") == "set_activity" and action.get("element") == element:
                        return action.get("level", "unknown")

        return "baseline"  # Default activity if no rules apply

    def _rule_applies_to_element(self, condition, element):
        """Check if a rule condition applies to a specific element."""
        if not condition:
            return False

        # Handle list of conditions (any condition that applies to the element)
        if isinstance(condition, list):
            return any(self._rule_applies_to_element(c, element) for c in condition)

        condition_type = condition.get("type")

        if condition_type == "is_within":
            return condition.get("element") == element
        elif condition_type == "distance_between":
            return condition.get("element_a") == element or condition.get("element_b") == element
        elif condition_type == "is_in_contact":
            return condition.get("element_a") == element or condition.get("element_b") == element
        elif condition_type == "logical":
            left_applies = self._rule_applies_to_element(condition.get("left"), element)
            right_applies = self._rule_applies_to_element(condition.get("right"), element)
            return left_applies or right_applies
        elif condition_type == "not":
            return self._rule_applies_to_element(condition.get("condition"), element)

        return False

    def evaluate_expression(self, node):
        """Evaluate expressions supported by the demo interpreter."""
        if node is None:
            return None
        t = node.get("type")
        if t in {"string_literal", "number_literal", "boolean_literal"}:
            return node.get("value")
        if t == "variable_access":
            name = node["name"]
            if name in self.symbol_table:
                return self.symbol_table[name]
            raise NameError(f"Undefined variable '{name}'")
        if t == "binary_operation":
            left = self.evaluate_expression(node["left"])
            right = self.evaluate_expression(node["right"])
            op = node["operator"]
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                return left / right
            if op == "&":
                return str(left) + str(right)
            if op == "==":
                return left == right
            if op == ">":
                return left > right
            if op == "<":
                return left < right
            if op == ">=":
                return left >= right
            if op == "<=":
                return left <= right
            if str(op).upper() == "AND":
                return bool(left) and bool(right)
            if str(op).upper() == "OR":
                return bool(left) or bool(right)
            raise ValueError(f"Unsupported binary operator: {op}")
        if t == "unary_operation":
            operand = self.evaluate_expression(node["operand"])
            op = node["operator"]
            if str(op).upper() == "NOT":
                return not bool(operand)
            raise ValueError(f"Unsupported unary operator: {op}")
        if t == "array_literal":
            return [self.evaluate_expression(e) for e in node.get("elements", [])]
        if t == "object_literal":
            return {k: self.evaluate_expression(v) for k, v in node.get("properties", {}).items()}
        if t == "access_chain":
            base_value = self.evaluate_expression(node["base"])
            for accessor in node["accessors"]:
                if accessor["type"] == "property_access":
                    prop_name = accessor["name"]
                    if isinstance(base_value, dict) and prop_name in base_value:
                        base_value = base_value[prop_name]
                    else:
                        raise AttributeError(f"Cannot access property '{prop_name}'")
                elif accessor["type"] == "index_access":
                    index_value = self.evaluate_expression(accessor["index"])
                    if isinstance(base_value, (list, str)) and isinstance(index_value, int):
                        if 0 <= index_value < len(base_value):
                            base_value = base_value[index_value]
                        else:
                            raise IndexError(f"Index {index_value} out of bounds")
                    else:
                        raise TypeError("Invalid index operation")
            return base_value
        raise ValueError(f"Unknown expression type: {t}")


__all__ = ["Interpreter"]
