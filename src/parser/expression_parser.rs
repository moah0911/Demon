//! Expression parsing for the Demon language.

use super::*;
use crate::lexer::TokenType::*;

impl<'a> Parser<'a> {
    /// Parses an expression.
    pub fn expression(&mut self) -> Result<Expr> {
        self.assignment()
    }

    /// Parses an assignment expression.
    fn assignment(&mut self) -> Result<Expr> {
        let expr = self.or()?;

        if self.match_tokens(&[Equal]) {
            let equals = self.previous().clone();
            let value = self.assignment()?;

            if let Expr::Variable(name) = expr {
                return Ok(Expr::Assign {
                    name: name.clone(),
                    value: Box::new(value),
                });
            } else if let Expr::Get { object, name } = expr {
                return Ok(Expr::Set {
                    object,
                    name: name.clone(),
                    value: Box::new(value),
                });
            }

            return Err(Error::Parse(parse_error(&equals, "Invalid assignment target.")));
        }

        Ok(expr)
    }

    /// Parses a logical OR expression.
    fn or(&mut self) -> Result<Expr> {
        let mut expr = self.and()?;

        while self.match_tokens(&[Or]) {
            let operator = self.previous().clone();
            let right = self.and()?;
            expr = Expr::Logical {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    /// Parses a logical AND expression.
    fn and(&mut self) -> Result<Expr> {
        let mut expr = self.equality()?;

        while self.match_tokens(&[And]) {
            let operator = self.previous().clone();
            let right = self.equality()?;
            expr = Expr::Logical {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    /// Parses an equality expression.
    fn equality(&mut self) -> Result<Expr> {
        self.binary_expression(Self::comparison, &[BangEqual, EqualEqual])
    }

    /// Parses a comparison expression.
    fn comparison(&mut self) -> Result<Expr> {
        self.binary_expression(Self::term, &[Greater, GreaterEqual, Less, LessEqual])
    }

    /// Parses a term expression (addition or subtraction).
    fn term(&mut self) -> Result<Expr> {
        self.binary_expression(Self::factor, &[Minus, Plus])
    }

    /// Parses a factor expression (multiplication or division).
    fn factor(&mut self) -> Result<Expr> {
        self.binary_expression(Self::unary, &[Slash, Star])
    }

    /// A helper function for binary expressions.
    fn binary_expression<F>(&mut self, next_fn: F, operators: &[TokenType]) -> Result<Expr>
    where
        F: Fn(&mut Self) -> Result<Expr>,
    {
        let mut expr = next_fn(self)?;

        while self.match_tokens(operators) {
            let operator = self.previous().clone();
            let right = next_fn(self)?;
            expr = Expr::Binary {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    /// Parses a unary expression.
    pub(super) fn unary(&mut self) -> Result<Expr> {
        if self.match_tokens(&[TokenType::Bang, TokenType::Minus, TokenType::Star, TokenType::Ampersand]) {
            let operator = self.previous().clone();
            let right = self.unary()?;
            
            // Handle pointer dereference (*) and address-of (&) operators
            match operator.token_type {
                TokenType::Star => Ok(Expr::Dereference {
                    expression: Box::new(right),
                }),
                TokenType::Ampersand => Ok(Expr::AddressOf {
                    expression: Box::new(right),
                }),
                _ => Ok(Expr::Unary {
                    operator,
                    right: Box::new(right),
                }),
            }
        } else {
            self.call()
        }
    }

    /// Parses a function call or primary expression.
    pub(super) fn call(&mut self) -> Result<Expr> {
        let mut expr = self.primary()?;

        loop {
            if self.match_tokens(&[TokenType::LeftParen]) {
                expr = self.finish_call(expr)?;
            } else if self.match_tokens(&[TokenType::Dot]) {
                let name = if let Some(token) = self.match_identifier() {
                    token
                } else {
                    return Err(Error::Parse(ParseError::Custom(
                        "Expect property name after '.'.".to_string(),
                    )));
                };
                expr = Expr::Get {
                    object: Box::new(expr),
                    name: name.clone(),
                };
            } else if self.match_tokens(&[TokenType::LeftBrace]) {
                // Array access: expr[expr]
                let index = self.expression()?;
                self.consume(TokenType::RightBrace, "Expect ']' after index.")?;
                expr = Expr::ArrayAccess {
                    array: Box::new(expr),
                    index: Box::new(index),
                };
            } else {
                break;
            }
        }

        Ok(expr)
    }

    /// Finishes parsing a function call.
    fn finish_call(&mut self, callee: Expr) -> Result<Expr> {
        let mut arguments = Vec::new();

        if !self.check(&RightParen) {
            loop {
                if arguments.len() >= 255 {
                    return Err(Error::Parse(parse_error(
                        self.peek(),
                        "Cannot have more than 255 arguments.",
                    )));
                }
                arguments.push(self.expression()?);

                if !self.match_tokens(&[Comma]) {
                    break;
                }
            }
        }

        self.consume(RightParen, "Expect ')' after arguments.")?;

        Ok(Expr::Call {
            callee: Box::new(callee),
            arguments,
        })
    }

    /// Parses a primary expression.
    pub(super) fn primary(&mut self) -> Result<Expr> {
        // Check for 'new' keyword first
        if self.match_tokens(&[TokenType::New]) {
            return self.new_expression();
        }
        
        // Check for 'delete' keyword
        if self.match_tokens(&[TokenType::Delete]) {
            let target = self.unary()?;  // Parse the target to delete
            
            // Check for array delete (delete[])
            if self.match_tokens(&[TokenType::LeftBrace]) {
                self.consume(TokenType::RightBrace, "Expect ']' after 'delete'.")?;
                return Ok(Expr::DeleteArray {
                    target: Box::new(target),
                });
            }
            
            return Ok(Expr::Delete {
                target: Box::new(target),
            });
        }

        if self.match_tokens(&[TokenType::False]) {
            Ok(Expr::Literal(self.previous().clone()))
        } else if self.match_tokens(&[TokenType::True]) {
            Ok(Expr::Literal(self.previous().clone()))
        } else if self.match_tokens(&[TokenType::Nil]) {
            Ok(Expr::Literal(self.previous().clone()))
        } else if let Some(token) = self.match_number() {
            Ok(Expr::Literal(token))
        } else if let Some(token) = self.match_string() {
            Ok(Expr::Literal(token))
        } else if self.match_tokens(&[TokenType::LeftParen]) {
            let expr = self.expression()?;
            self.consume(TokenType::RightParen, "Expect ')' after expression.")?;
            Ok(Expr::Grouping(Box::new(expr)))
        } else if let Some(ident) = self.match_identifier() {
            Ok(Expr::Variable(ident))
        } else if self.match_tokens(&[TokenType::This]) {
            Ok(Expr::This(self.previous().clone()))
        } else if self.match_tokens(&[TokenType::Super]) {
            let keyword = self.previous().clone();
            self.consume(TokenType::Dot, "Expect '.' after 'super'.")?;
            let method = if let Some(ident) = self.match_identifier() {
                ident
            } else {
                return Err(Error::Parse(ParseError::Custom("Expect superclass method name.".to_string())));
            };
            Ok(Expr::Super { 
                keyword: keyword.clone(), 
                method: method.clone() 
            })
        } else {
            Err(Error::Parse(ParseError::Custom(
                format!("Expect expression, found '{}'.", self.peek().lexeme)
            )))
        }
    }
    
    /// Parses a 'new' expression.
    /// Parses a comma-separated list of arguments.
    fn argument_list(&mut self) -> Result<Vec<Expr>> {
        let mut arguments = Vec::new();
        
        if !self.check(&TokenType::RightParen) {
            loop {
                if arguments.len() >= 255 {
                    return Err(Error::Parse(ParseError::Custom(
                        "Cannot have more than 255 arguments.".to_string(),
                    )));
                }
                
                arguments.push(self.expression()?);
                
                if !self.match_tokens(&[TokenType::Comma]) {
                    break;
                }
            }
        }
        
        self.consume(TokenType::RightParen, "Expect ')' after arguments.")?;
        Ok(arguments)
    }
    
    /// Parses a 'new' expression.
    fn new_expression(&mut self) -> Result<Expr> {
        // Check for custom allocator: new(allocator) Type()
        if self.match_tokens(&[TokenType::LeftParen]) {
            let allocator = self.expression()?;
            self.consume(TokenType::RightParen, "Expect ')' after allocator expression.")?;
            
            let class = self.primary()?;
            let arguments = if self.match_tokens(&[TokenType::LeftParen]) {
                self.argument_list()?
            } else {
                Vec::new()
            };
            
            return Ok(Expr::CustomNew {
                allocator: Box::new(allocator),
                class: Box::new(class),
                arguments,
            });
        }
        
        // Check for array allocation: new Type[size]
        if self.match_tokens(&[TokenType::LeftBrace]) {
            let element_type = self.previous().clone();
            let size = self.expression()?;
            self.consume(TokenType::RightBrace, "Expect ']' after array size.")?;
            
            return Ok(Expr::NewArray {
                element_type,
                size: Box::new(size),
            });
        }
        
        // Regular object allocation: new Type()
        let class = self.primary()?;
        let arguments = if self.match_tokens(&[TokenType::LeftParen]) {
            self.argument_list()?
        } else {
            Vec::new()
        };
        
        Ok(Expr::New {
            class: Box::new(class),
            arguments,
        })
    }
}
