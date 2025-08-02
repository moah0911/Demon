//! Statement parsing for the Demon language.

use super::*;
use crate::lexer::TokenType::*;

impl<'a> Parser<'a> {
    /// Parses a declaration.
    pub fn declaration(&mut self) -> Result<Option<Stmt>> {
        let result = if self.match_tokens(&[Var]) {
            self.var_declaration()
        } else if self.match_tokens(&[Const]) {
            self.const_declaration()
        } else if self.match_tokens(&[Func]) {
            self.function("function").map(Some)
        } else if self.match_tokens(&[Class]) {
            self.class_declaration()
        } else {
            self.statement()
        };

        if result.is_err() {
            self.synchronize();
        }

        result
    }

    /// Parses a variable declaration.
    fn var_declaration(&mut self) -> Result<Option<Stmt>> {
        // Get the name first and store it in a temporary variable
        let name = {
            let name_token = self.consume(
                TokenType::Identifier("".to_string()),
                "Expect variable name.",
            )?;
            name_token.clone()
        };

        // Check for initializer
        let has_initializer = self.match_tokens(&[Equal]);
        let initializer = if has_initializer {
            let expr = self.expression()?;
            Some(expr)
        } else {
            None
        };

        // Consume the semicolon
        self.consume(
            Semicolon,
            "Expect ';' after variable declaration.",
        )?;

        Ok(Some(Stmt::Var { 
            name, 
            initializer 
        }))
    }

    /// Parses a constant declaration.
    fn const_declaration(&mut self) -> Result<Option<Stmt>> {
        // Get the name first and store it in a temporary variable
        let name = {
            let name_token = self.consume(
                TokenType::Identifier("".to_string()),
                "Expect constant name.",
            )?;
            name_token.clone()
        };

        // Consume the equals sign
        self.consume(Equal, "Expect '=' after constant name.")?;
        
        // Get the initializer expression
        let initializer = self.expression()?;
        
        // Consume the semicolon
        self.consume(
            Semicolon,
            "Expect ';' after constant declaration.",
        )?;

        Ok(Some(Stmt::Const { 
            name,
            initializer 
        }))
    }

    /// Parses a statement.
    fn statement(&mut self) -> Result<Option<Stmt>> {
        if self.match_tokens(&[Print]) {
            self.print_statement()
        } else if self.match_tokens(&[LeftBrace]) {
            Ok(Some(Stmt::Block(self.block()?)))
        } else if self.match_tokens(&[If]) {
            self.if_statement()
        } else if self.match_tokens(&[While]) {
            self.while_statement()
        } else if self.match_tokens(&[For]) {
            self.for_statement()
        } else if self.match_tokens(&[Return]) {
            self.return_statement()
        } else {
            if self.match_tokens(&[Semicolon]) {
                Ok(Some(Stmt::Empty))
            } else {
                self.expression_statement().map(Some)
            }
        }
    }

    /// Parses a print statement.
    fn print_statement(&mut self) -> Result<Option<Stmt>> {
        let value = self.expression()?;
        self.consume(Semicolon, "Expect ';' after value.")?;
        Ok(Some(Stmt::Print(value)))
    }

    /// Parses an expression statement.
    fn expression_statement(&mut self) -> Result<Stmt> {
        let expr = self.expression()?;
        self.consume(Semicolon, "Expect ';' after expression.")?;
        Ok(Stmt::Expression(expr))
    }

    /// Parses a block of statements.
    fn block(&mut self) -> Result<Vec<Stmt>> {
        let mut statements = Vec::new();

        while !self.check(&RightBrace) && !self.is_at_end() {
            if let Some(decl) = self.declaration()? {
                statements.push(decl);
            }
        }

        self.consume(RightBrace, "Expect '}' after block.")?;
        Ok(statements)
    }

    /// Parses an if statement.
    fn if_statement(&mut self) -> Result<Option<Stmt>> {
        self.consume(LeftParen, "Expect '(' after 'if'.")?;
        let condition = self.expression()?;
        self.consume(RightParen, "Expect ')' after if condition.")?;

        let then_branch = Box::new(
            self.statement()?
                .ok_or_else(|| Error::Parse(ParseError::Custom(
                    format!("{} at '{}'", "Expect statement after 'if'.", self.peek().lexeme)
                )))?,
        );

        let else_branch = if self.match_tokens(&[Else]) {
            Some(Box::new(
                self.statement()?.ok_or_else(|| {
                    Error::Parse(ParseError::Custom(
                        format!("{} at '{}'", "Expect statement after 'else'.", self.peek().lexeme)
                    ))
                })?,
            ))
        } else {
            None
        };

        Ok(Some(Stmt::If {
            condition,
            then_branch,
            else_branch,
        }))
    }

    /// Parses a while statement.
    fn while_statement(&mut self) -> Result<Option<Stmt>> {
        self.consume(LeftParen, "Expect '(' after 'while'.")?;
        let condition = self.expression()?;
        self.consume(RightParen, "Expect ')' after condition.")?;

        let body = Box::new(
            self.statement()?
                .ok_or_else(|| Error::Parse(ParseError::Custom(
                    format!("{} at '{}'", "Expect statement after 'while'.", self.peek().lexeme)
                )))?,
        );

        Ok(Some(Stmt::While { condition, body }))
    }

    /// Parses a for statement.
    fn for_statement(&mut self) -> Result<Option<Stmt>> {
        self.consume(LeftParen, "Expect '(' after 'for'.")?;

        // Initializer
        let initializer = if self.match_tokens(&[Semicolon]) {
            None
        } else if self.match_tokens(&[Var]) {
            self.var_declaration()?
        } else if self.match_tokens(&[Const]) {
            self.const_declaration()?
        } else {
            Some(self.expression_statement()?)
        };

        // Condition
        let condition = if !self.check(&Semicolon) {
            self.expression()
        } else {
            // Default to true if condition is omitted
            Ok(Expr::Literal(Token::new(
                TokenType::True,
                "true".to_string(),
                self.previous().line,
            )))
        }?;

        self.consume(Semicolon, "Expect ';' after loop condition.")?;

        // Increment
        let increment = if !self.check(&RightParen) {
            let expr = self.expression()?;
            Some(expr)
        } else {
            None
        };

        self.consume(RightParen, "Expect ')' after for clauses.")?;

        let mut body = self.statement()?;

        // Desugar the for loop into a while loop
        if let Some(inc) = increment {
            if let Some(stmt) = &mut body {
                // Wrap the body in a block with the increment at the end
                let nil_token = Token::new(TokenType::Nil, "nil".to_string(), self.previous().line);
                let old_stmt = std::mem::replace(stmt, Stmt::Expression(Expr::Literal(nil_token)));
                *stmt = Stmt::Block(vec![old_stmt, Stmt::Expression(inc)]);
            }
        }

        let while_loop = Stmt::While {
            condition,
            body: Box::new(body.unwrap_or_else(|| {
                let nil_token = Token::new(TokenType::Nil, "nil".to_string(), self.previous().line);
                Stmt::Expression(Expr::Literal(nil_token))
            })),
        };

        let result = if let Some(init) = initializer {
            Stmt::Block(vec![init, while_loop])
        } else {
            while_loop
        };

        Ok(Some(result))
    }

    /// Parses a function declaration.
    fn function(&mut self, kind: &str) -> Result<Stmt> {
        let name = self.consume(
            TokenType::Identifier("".to_string()),
            &format!("Expect {} name.", kind),
        )?.clone();

        self.consume(
            LeftParen,
            &format!("Expect '(' after {} name.", kind),
        )?;

        let mut parameters = Vec::new();
        if !self.check(&RightParen) {
            loop {
                if parameters.len() >= 255 {
                    return Err(Error::Parse(ParseError::Custom(
                        format!("{} at '{}'", "Cannot have more than 255 parameters.", self.peek().lexeme)
                    )));
                }

                parameters.push(
                    self.consume(
                        TokenType::Identifier("".to_string()),
                        "Expect parameter name.",
                    )?
                    .clone(),
                );

                if !self.match_tokens(&[Comma]) {
                    break;
                }
            }
        }

        self.consume(RightParen, "Expect ')' after parameters.")?;
        self.consume(LeftBrace, &format!("Expect '{{' before {} body.", kind))?;

        let body = self.block()?;
        Ok(Stmt::Function {
            name,
            params: parameters,
            body,
        })
    }

    /// Parses a class declaration.
    fn class_declaration(&mut self) -> Result<Option<Stmt>> {
        // Get the name first and store it in a temporary variable
        let name = {
            let name_token = self.consume(
                TokenType::Identifier("".to_string()),
                "Expect class name.",
            )?;
            name_token.clone()
        };

        let superclass = if self.match_tokens(&[Less]) {
            self.consume(Identifier("".to_string()), "Expect superclass name.")?;
            Some(Expr::Variable(self.previous().clone()))
        } else {
            None
        };

        self.consume(LeftBrace, "Expect '{' before class body.")?;

        let mut methods = Vec::new();
        while !self.check(&RightBrace) && !self.is_at_end() {
            methods.push(self.function("method")?);
        }

        self.consume(RightBrace, "Expect '}' after class body.")?;

        Ok(Some(Stmt::Class { name, superclass, methods }))
    }

    /// Parses a return statement.
    fn return_statement(&mut self) -> Result<Option<Stmt>> {
        let keyword = self.previous().clone();
        let value = if !self.check(&Semicolon) {
            Some(self.expression()?)
        } else {
            None
        };

        self.consume(Semicolon, "Expect ';' after return value.")?;
        Ok(Some(Stmt::Return { keyword, value }))
    }

    /// Synchronizes the parser after a syntax error.
    fn synchronize(&mut self) {
        self.advance();

        while !self.is_at_end() {
            if self.previous().token_type == Semicolon {
                return;
            }

            match &self.peek().token_type {
                Var | Const | For | If | While | Print | Return | Func | Class => return,
                _ => {}
            }

            self.advance();
        }
    }
}
